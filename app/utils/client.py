# app/utils/client.py
"""
Client interne pour appeler les routes API depuis les routes FRONT.
Fournit : GET / POST / PUT / PATCH / DELETE
Utilise httpx pour envoyer des requêtes internes au serveur.
"""

import httpx
from typing import Any, Dict, Optional
from utils.logger import get_logger
import config

logger = get_logger(__name__)

API_BASE = config.API_BASE_URL  # à adapter si reverse-proxy


def _build_headers(token: Optional[str] = None) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def api_get(path: str, token: Optional[str] = None) -> Any:
    url = f"{API_BASE}{path}"
    logger.debug(f"[api_get] GET {url}")

    with httpx.Client() as client:
        resp = client.get(url, headers=_build_headers(token))
        resp.raise_for_status()
        return resp.json()


def api_post(path: str, data: Dict[str, Any] = None, token: Optional[str] = None) -> Any:
    url = f"{API_BASE}{path}"
    logger.debug(f"[api_post] POST {url} data={data}")

    with httpx.Client() as client:
        resp = client.post(url, json=data or {}, headers=_build_headers(token))
        resp.raise_for_status()
        return resp.json()


def api_put(path: str, data: Dict[str, Any] = None, token: Optional[str] = None) -> Any:
    url = f"{API_BASE}{path}"
    logger.debug(f"[api_put] PUT {url} data={data}")

    with httpx.Client() as client:
        resp = client.put(url, json=data or {}, headers=_build_headers(token))
        resp.raise_for_status()
        return resp.json()


def api_patch(path: str, data: Dict[str, Any] = None, token: Optional[str] = None) -> Any:
    url = f"{API_BASE}{path}"
    logger.debug(f"[api_patch] PATCH {url} data={data}")

    with httpx.Client() as client:
        resp = client.patch(url, json=data or {}, headers=_build_headers(token))
        resp.raise_for_status()
        return resp.json()


def api_delete(path: str, token: Optional[str] = None) -> Any:
    url = f"{API_BASE}{path}"
    logger.debug(f"[api_delete] DELETE {url}")

    with httpx.Client() as client:
        resp = client.delete(url, headers=_build_headers(token))
        resp.raise_for_status()
        return resp.json()
