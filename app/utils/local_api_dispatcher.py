# app/utils/local_api_dispatcher.py
"""
Local API dispatcher — auto-discovery, async-safe, cache, logging.
Supporte GET/POST/PUT/PATCH/DELETE.

Usage:
    await call_local_async("/api/public/professions", method="GET", params=..., body=...)
    call_local_sync("/api/public/professions", method="POST", body={...})
"""

from __future__ import annotations
import inspect
import importlib
import pkgutil
import anyio
import asyncio
import time
import json
from typing import Any, Callable, Dict, Optional, Tuple

# Prefer project's logger if available
try:
    from utils.logger import get_logger
    logger = get_logger(__name__)
except Exception:
    import logging
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

# Where to scan routers — adapte si nécessaire
API_ROUTER_IMPORT_PATH = "routes.api"

# Registry: (METHOD, PATH) -> handler
LOCAL_REGISTRY: Dict[Tuple[str, str], Callable[..., Any]] = {}

# Simple TTL cache
_CACHE: Dict[str, Tuple[float, Any]] = {}


def _normalize(path: str) -> str:
    return (path.rstrip("/") or "/")


def _register(method: str, path: str, handler: Callable[..., Any]) -> None:
    key = (method.upper(), _normalize(path))
    LOCAL_REGISTRY[key] = handler
    logger.debug(f"[dispatcher] registered {method.upper()} {path} -> {handler}")


def _scan_package_for_routers():
    """
    Best-effort scan of modules under API_ROUTER_IMPORT_PATH to discover route objects.
    Register their endpoints into LOCAL_REGISTRY.
    """
    try:
        pkg = importlib.import_module(API_ROUTER_IMPORT_PATH)
    except Exception as e:
        logger.warning(f"[dispatcher] cannot import {API_ROUTER_IMPORT_PATH}: {e}")
        return

    # iterate modules under package
    for finder, modname, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        try:
            mod = importlib.import_module(modname)
        except Exception as e:
            logger.debug(f"[dispatcher] skip {modname}: import error {e}")
            continue

        # look for objects with .routes attribute (FastAPI/APIRouter)
        for attr in dir(mod):
            obj = getattr(mod, attr, None)
            if not obj:
                continue
            if not hasattr(obj, "routes"):
                continue
            try:
                for route in getattr(obj, "routes") or []:
                    path = getattr(route, "path", None)
                    methods = getattr(route, "methods", None)
                    endpoint = getattr(route, "endpoint", None)
                    if not path or not methods or not endpoint:
                        continue
                    # register all methods (including PATCH)
                    for m in methods:
                        if m.upper() in ("HEAD", "OPTIONS"):
                            continue
                        _register(m.upper(), path, endpoint)
            except Exception as e:
                logger.debug(f"[dispatcher] fail scan in {mod}.{attr}: {e}")

    logger.info(f"[dispatcher] scan complete — {len(LOCAL_REGISTRY)} endpoints registered")


# build registry on import
_scan_package_for_routers()


# ---------------- CACHE ----------------
def cache_set(key: str, value: Any, ttl: int = 0) -> None:
    if ttl > 0:
        _CACHE[key] = (time.time() + ttl, value)
    else:
        _CACHE[key] = (0.0, value)


def cache_get(key: str) -> Optional[Any]:
    ent = _CACHE.get(key)
    if not ent:
        return None
    exp, val = ent
    if exp and exp < time.time():
        del _CACHE[key]
        return None
    return val


def _cache_key(method: str, path: str, params: Optional[Dict] = None, body: Optional[Any] = None) -> str:
    key = f"{method.upper()} {path}"
    if params:
        key += " params:" + json.dumps(params, sort_keys=True, default=str)
    if body:
        key += " body:" + json.dumps(body, sort_keys=True, default=str)
    return key


# ---------------- CALL HANDLERS ----------------
async def call_local_async(
    path: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Any] = None,
    request = None,
    cache_ttl: int = 0
) -> Any:
    """
    Async call to local handler.
    - supports async handler (awaits) or sync (runs in thread)
    - maps params/body to handler signature by name
    - optional cache for GET
    """
    method = method.upper()
    path_norm = _normalize(path)
    key = (method, path_norm)

    # caching
    cache_k = _cache_key(method, path_norm, params, body)
    if cache_ttl and method == "GET":
        cached = cache_get(cache_k)
        if cached is not None:
            logger.debug(f"[dispatcher] cache hit {method} {path_norm}")
            return cached

    handler = LOCAL_REGISTRY.get(key)
    if not handler:
        raise KeyError(f"No local handler for {method} {path_norm}")

    # build kwargs for handler
    sig = inspect.signature(handler)
    kwargs = {}
    for pname, p in sig.parameters.items():
        if pname in ("request", "req") and request is not None:
            kwargs[pname] = request
            continue
        if params and pname in params:
            kwargs[pname] = params[pname]
            continue
        if body and isinstance(body, dict) and pname in body:
            kwargs[pname] = body[pname]
            continue
        if p.default is not inspect._empty:
            kwargs[pname] = p.default

    logger.debug(f"[dispatcher] calling {method} {path_norm} -> {handler} with {list(kwargs.keys())}")

    try:
        if inspect.iscoroutinefunction(handler):
            res = await handler(**kwargs)
        else:
            # run sync handler in thread to not block event loop
            res = await anyio.to_thread.run_sync(lambda: handler(**kwargs))
    except Exception as e:
        logger.exception(f"[dispatcher] handler exception for {method} {path_norm}: {e}")
        raise

    if cache_ttl and method == "GET":
        try:
            cache_set(cache_k, res, ttl=cache_ttl)
        except Exception:
            logger.debug("[dispatcher] could not cache (non serializable)")

    return res


def call_local_sync(path: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, body: Optional[Any] = None, request=None, cache_ttl: int = 0) -> Any:
    return anyio.run(call_local_async, path, method, params, body, request, cache_ttl)


# ---------------- Registry export ----------------
def export_registry(path_out: str, fmt: str = "json"):
    data = []
    for (m, p), handler in LOCAL_REGISTRY.items():
        data.append({"method": m, "path": p, "handler": f"{handler.__module__}.{handler.__name__}"})
    if fmt == "json":
        with open(path_out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif fmt == "py":
        with open(path_out, "w", encoding="utf-8") as f:
            f.write("# Auto-exported local registry\nROUTES = [\n")
            for item in data:
                f.write(f"    {item!r},\n")
            f.write("]\n")
    else:
        raise ValueError("fmt=json|py")
    logger.info(f"[dispatcher] exported registry to {path_out}")
