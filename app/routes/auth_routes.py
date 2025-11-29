# app/routes/auth_routes.py
"""
Chemin : app/routes/auth_routes.py

Routes d'authentification.
Compatible avec :
 - utils/auth.py (version sécurisée avec refresh tokens hashés)
 - utils/json
 - utils.deps.get_current_user_required
 - utils.roles.require_admin

Fonctions principales :
 - POST /api/auth/login
 - POST /api/auth/refresh
 - POST /api/auth/logout
 - POST /api/auth/logout_all
 - GET  /api/auth/me/devices
 - POST /api/auth/me/devices/{device_id}/revoke

Après mise à jour :
 - Utilise rotate_refresh_token() pour une rotation sécurisée
"""

from fastapi import APIRouter, Body, Request, Response, HTTPException, Depends
from typing import Dict, Any, Optional
from uuid import uuid4

from config import USERS_FILE, REFRESH_TOKENS_FILE, REFRESH_TOKEN_EXPIRE_DAYS

from utils.json import load_json, save_json
from utils.auth import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_access_token,
    verify_password,
    store_refresh_token,
    revoke_refresh_token,
    revoke_all_tokens_for_user,
    get_active_devices,
    rotate_refresh_token,   # ← nouvelle fonction utilisée partout
)
from utils.deps import get_current_user_required
from utils.roles import require_admin

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _find_user_by_login(login: str) -> Optional[Dict[str, Any]]:
    users = load_json(USERS_FILE) or {}
    for uid, u in users.items():
        if u.get("login") == login:
            user = dict(u)
            user["id"] = uid
            return user
    return None


# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------
@router.post("/login")
def login(payload: Dict[str, Any] = Body(...), response: Response = None):
    """
    Payload: { login, password, device_id? }
    Returns { access_token, user }
    + HTTP-only cookie refresh_token
    """
    login_val = payload.get("login") or payload.get("username")
    password = payload.get("password")
    device_id = payload.get("device_id") or str(uuid4())
    device_name = payload.get("device_name") or ""  # optionnel

    if not login_val or not password:
        raise HTTPException(status_code=400, detail="Missing login or password")

    user = _find_user_by_login(login_val)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens
    uid = user["id"]
    access = create_access_token({"sub": uid})
    refresh = create_refresh_token({"sub": uid})

    # Store (HMAC-hash only)
    store_refresh_token(refresh, uid, device_id, device_name)

    # Prepare safe user
    safe_user = dict(user)
    safe_user.pop("password_hash", None)

    # Set secure cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=True,            # SSL recommended
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    return {
        "access_token": access,
        "device_id": device_id,
        "device_name": device_name,
        "user": safe_user,
    }


# ---------------------------------------------------------------------------
# REFRESH — NOW USING rotate_refresh_token()
# ---------------------------------------------------------------------------
@router.post("/refresh")
def refresh(body: Dict[str, Any] = Body(...), response: Response = None):
    """
    Payload: { refresh_token }
    Rotate:
      - verify refresh
      - revoke old token
      - generate new tokens
      - save new refresh for same device
      - set cookie again
    """
    old_refresh = body.get("refresh_token")
    if not old_refresh:
        raise HTTPException(status_code=400, detail="Missing refresh_token")

    old_payload = decode_refresh_token(old_refresh)
    if not old_payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    uid = old_payload.get("sub")
    if not uid:
        raise HTTPException(status_code=400, detail="Malformed token")

    store = load_json(REFRESH_TOKENS_FILE) or {}
    # store uses hashed keys, so check through HMAC hash
    # → use rotate helper instead of checking store directly

    # Create new tokens
    new_access = create_access_token({"sub": uid})
    new_refresh = create_refresh_token({"sub": uid})

    # We need device_id : get it from store via raw hashed lookup
    # Instead of calling internal hash, we parse devices:
    devices = get_active_devices(uid)
    # Try to find the device by matching token hash
    device_id = None
    for d in devices:
        # d["token_hash"] is hashed token but we don't have hashed(old_refresh) directly here
        # → API changed : we must hash old_refresh for matching
        from utils.auth import _token_hash
        if d["token_hash"] == _token_hash(old_refresh):
            device_id = d["device_id"]
            break

    if not device_id:
        # fallback (rare): assign a new device_id
        device_id = str(uuid4())

    # ROTATE: atomic revoke + store
    rotate_refresh_token(old_refresh, new_refresh, uid, device_id)

    # Set updated cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "device_id": device_id,
    }


# ---------------------------------------------------------------------------
# LOGOUT — revoke only this device
# ---------------------------------------------------------------------------
@router.post("/logout")
def logout(request: Request, body: Dict[str, Any] = Body(None)):
    """
    Revoke only the current device's refresh token.
    Accepts token in body or cookie.
    """
    refresh_token = (
        (body.get("refresh_token") if body else None)
        or request.cookies.get("refresh_token")
    )

    if refresh_token:
        try:
            revoke_refresh_token(refresh_token)
        except Exception:
            pass

    # Cookie cleanup
    resp = {"message": "Logged out"}
    return resp


# ---------------------------------------------------------------------------
# LOGOUT ALL — revoke alllll sessions of user
# ---------------------------------------------------------------------------
@router.post("/logout_all")
def logout_all(user = Depends(get_current_user_required)):
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    if not uid:
        raise HTTPException(status_code=400, detail="Invalid user")
    revoke_all_tokens_for_user(uid)
    return {"message": "All sessions revoked"}


# ---------------------------------------------------------------------------
# DEVICE LIST
# ---------------------------------------------------------------------------
@router.get("/me/devices")
def list_devices(user = Depends(get_current_user_required)):
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    if not uid:
        raise HTTPException(status_code=400, detail="Invalid user")

    return {"devices": get_active_devices(uid)}


# ---------------------------------------------------------------------------
# DEVICE REVOKE
# ---------------------------------------------------------------------------
@router.post("/me/devices/{device_id}/revoke")
def revoke_device(device_id: str, user = Depends(get_current_user_required)):
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    if not uid:
        raise HTTPException(status_code=400, detail="Invalid user")

    # Remove tokens matching the device (hashed store)
    store = load_json(REFRESH_TOKENS_FILE) or {}
    to_delete = []

    # Need to check hashed entries
    for token_hash, meta in store.items():
        if meta.get("user_id") == uid and meta.get("device_id") == device_id:
            to_delete.append(token_hash)

    for th in to_delete:
        store.pop(th, None)

    save_json(REFRESH_TOKENS_FILE, store)

    return {"revoked": len(to_delete)}
