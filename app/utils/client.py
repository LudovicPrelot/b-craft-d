# app/utils/client.py
"""
Client wrapper : HTTP first, fallback local via local_api_dispatcher.
Expose : api_get, api_post, api_put, api_patch, api_delete (async).
Also sync wrappers sync_get, etc.
"""

from typing import Any, Dict, Optional
from fastapi import Request
import httpx
import anyio

import config
from utils.local_api_dispatcher import call_local_async, call_local_sync
from utils.logger import get_logger

logger = get_logger(__name__)

BASE_URL = config.API_BASE_URL.rstrip("/")
TIMEOUT = getattr(config, "HTTP_CLIENT_TIMEOUT", 8.0)
ENABLE_LOCAL_FALLBACK = getattr(config, "ENABLE_LOCAL_FALLBACK", True)


async def _try_refresh(request: Optional[Request]) -> Optional[str]:
    if not request:
        return None
    refresh = request.cookies.get("refresh_token")
    if not refresh:
        return None
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            resp = await c.post(f"{BASE_URL}/api/public/auth/refresh", json={"refresh_token": refresh})
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception:
        return None


async def _http_request(method: str, endpoint: str, *, request: Optional[Request] = None, params: Optional[Dict]=None, json_body: Optional[Dict]=None, auth_required: bool=False):
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {}
    cookies = None
    if request:
        cookies = request.cookies
        access = request.cookies.get("access_token")
        if access:
            headers["Authorization"] = f"Bearer {access}"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.request(method, url, params=params, json=json_body, headers=headers, cookies=cookies)

        # not-auth-required: let 401/403 pass back as result
        if not auth_required and resp.status_code in (401, 403):
            try:
                return resp.json()
            except Exception:
                return resp.text

        # auth_required but missing token -> raise
        if auth_required and not headers.get("Authorization"):
            raise PermissionError("Authentication required but no token found")

        # 401 -> try refresh once
        if resp.status_code == 401 and request:
            new_token = await _try_refresh(request)
            if new_token:
                headers["Authorization"] = f"Bearer {new_token}"
                async with httpx.AsyncClient(timeout=TIMEOUT) as client2:
                    r2 = await client2.request(method, url, params=params, json=json_body, headers=headers)
                r2.raise_for_status()
                return r2.json()

        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return resp.text

    except httpx.ConnectError as e:
        logger.debug(f"[client] connect error to {url}: {e}")
        # fallback local if enabled
        if ENABLE_LOCAL_FALLBACK:
            return await call_local_async(endpoint, method=method, params=params, body=json_body, request=request)
        raise

    except Exception as e:
        logger.exception(f"[client] http error: {e}")
        if ENABLE_LOCAL_FALLBACK:
            return await call_local_async(endpoint, method=method, params=params, body=json_body, request=request)
        raise


# async wrappers
async def api_get(endpoint: str, *, request: Optional[Request]=None, params: Optional[Dict]=None, auth_required: bool=False):
    return await _http_request("GET", endpoint, request=request, params=params, auth_required=auth_required)

async def api_post(endpoint: str, *, request: Optional[Request]=None, json: Optional[Dict]=None, auth_required: bool=False):
    return await _http_request("POST", endpoint, request=request, json_body=json, auth_required=auth_required)

async def api_put(endpoint: str, *, request: Optional[Request]=None, json: Optional[Dict]=None, auth_required: bool=False):
    return await _http_request("PUT", endpoint, request=request, json_body=json, auth_required=auth_required)

async def api_patch(endpoint: str, *, request: Optional[Request]=None, json: Optional[Dict]=None, auth_required: bool=False):
    return await _http_request("PATCH", endpoint, request=request, json_body=json, auth_required=auth_required)

async def api_delete(endpoint: str, *, request: Optional[Request]=None, params: Optional[Dict]=None, auth_required: bool=False):
    return await _http_request("DELETE", endpoint, request=request, params=params, auth_required=auth_required)


# sync wrappers for scripts/tests
def sync_get(endpoint: str, **kwargs):
    return anyio.run(api_get, endpoint, **kwargs)
def sync_post(endpoint: str, **kwargs):
    return anyio.run(api_post, endpoint, **kwargs)
def sync_put(endpoint: str, **kwargs):
    return anyio.run(api_put, endpoint, **kwargs)
def sync_patch(endpoint: str, **kwargs):
    return anyio.run(api_patch, endpoint, **kwargs)
def sync_delete(endpoint: str, **kwargs):
    return anyio.run(api_delete, endpoint, **kwargs)
