# app/utils/deps.py
"""
Dépendances communes (get current user, optional user).
- get_current_user_optional : ne lève pas si pas d'authentification, renvoie None.
- get_current_user_required : lève HTTP 401 si pas d'authentification.
"""

from fastapi import Depends, Header, HTTPException, status, Request
from typing import Optional, Dict, Any
from utils.logger import get_logger
from utils.json import load_json
import config
from utils.auth import decode_access_token

logger = get_logger(__name__)

USERS_FILE = config.USERS_FILE

# Try to load user by token payload
def _user_from_payload(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not payload:
        return None
    uid = payload.get("sub") or payload.get("user_id") or payload.get("id")
    if not uid:
        return None
    users = load_json(USERS_FILE) or {}
    user = users.get(uid)
    if not user:
        return None
    # ensure id key exists
    if isinstance(user, dict):
        user_copy = dict(user)
        user_copy["id"] = uid
        return user_copy
    return user


async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """
    Attempt to read Authorization header (Bearer) or cookies['access_token'].
    Returns user dict or None.
    """
    auth_header = request.headers.get("authorization")
    token = None
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        # try cookie
        token = request.cookies.get("access_token")

    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user = _user_from_payload(payload)
    return user


async def get_current_user_required(request: Request) -> Dict[str, Any]:
    """
    Return authenticated user or raise 401.
    """
    user = await get_current_user_optional(request)
    if not user:
        logger.info(f"Unauthorized access attempt: {request.client.host if request.client else 'unknown'} to {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user


def require_role(role_key: str, role_label: str):
    async def wrapper(user = Depends(get_current_user_required)):
        if not user.get(role_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role_label} privileges required"
            )
        return user
    return wrapper

get_current_moderator_required = require_role("is_moderator", "Moderator")
get_current_admin_required     = require_role("is_admin", "Admin")

