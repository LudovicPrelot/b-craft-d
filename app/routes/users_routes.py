# app/routes/users_routes.py
"""
Chemin : app/routes/users_routes.py

Routes CRUD pour les utilisateurs :
- POST /api/users           -> création (inscription)
- GET  /api/users/me        -> informations du user connecté
- GET  /api/users           -> liste (admin)
- GET  /api/users/{id}      -> lecture (admin)
- PUT  /api/users/{id}      -> modification (admin)
- DELETE /api/users/{id}    -> suppression (admin)

Utilise :
- utils.json.load_json / save_json
- utils.auth.hash_password
- dépendances : utils.deps.get_current_user_required
- rôles : utils.roles.require_admin
- config.USERS_FILE
"""

from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict, Any, Optional
from uuid import uuid4

import config
from utils.json import load_json, save_json
from utils.auth import hash_password
from utils.deps import get_current_user_required
from utils.roles import require_admin

router = APIRouter(prefix="/api/users", tags=["users"])

USERS_FILE = config.USERS_FILE

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def _load_users() -> Dict[str, Any]:
    return load_json(USERS_FILE) or {}

def _save_users(data: Dict[str, Any]) -> None:
    save_json(USERS_FILE, data)

# --------------------------------------------------------------------
# Create user (registration)
# --------------------------------------------------------------------
@router.post("/", status_code=201)
def create_user(payload: Dict[str, Any] = Body(...)):
    """
    Create a new user.
    Expected fields:
      - login (required)
      - password (required)
      - firstname, lastname, mail (optional)
      - profession, subclasses, is_admin, is_moderator (optional - admin only to set)
    """
    login = payload.get("login")
    password = payload.get("password")

    if not login or not password:
        raise HTTPException(status_code=400, detail="login and password required")

    users = _load_users()

    # ensure unique login
    for uid, u in users.items():
        if u.get("login") == login:
            raise HTTPException(status_code=400, detail="login already exists")

    uid = str(uuid4())
    user_obj = {
        "firstname": payload.get("firstname", ""),
        "lastname": payload.get("lastname", ""),
        "mail": payload.get("mail", ""),
        "login": login,
        "password_hash": hash_password(password),
        "profession": payload.get("profession", ""),
        "subclasses": payload.get("subclasses", []),
        "is_admin": bool(payload.get("is_admin", False)),
        "is_moderator": bool(payload.get("is_moderator", False))
    }
    users[uid] = user_obj
    _save_users(users)

    safe = dict(user_obj)
    safe.pop("password_hash", None)
    return {"id": uid, "user": safe}

# --------------------------------------------------------------------
# Current user
# --------------------------------------------------------------------
@router.get("/me")
def me(user = Depends(get_current_user_required)):
    """
    Return current user info (without password_hash).
    """
    # user can be dict or dataclass
    if isinstance(user, dict):
        safe = dict(user)
        safe.pop("password_hash", None)
        return safe
    # dataclass-like fallback
    try:
        return {
            "id": getattr(user, "id", None),
            "firstname": getattr(user, "firstname", ""),
            "lastname": getattr(user, "lastname", ""),
            "mail": getattr(user, "mail", ""),
            "login": getattr(user, "login", "")
        }
    except Exception:
        return {}

# --------------------------------------------------------------------
# Admin: list users
# --------------------------------------------------------------------
@router.get("/", dependencies=[Depends(require_admin)])
def list_users():
    users = _load_users()
    out = []
    for uid, u in users.items():
        safe = dict(u)
        safe.pop("password_hash", None)
        safe["id"] = uid
        out.append(safe)
    return out

# --------------------------------------------------------------------
# Admin: get user
# --------------------------------------------------------------------
@router.get("/{user_id}", dependencies=[Depends(require_admin)])
def get_user(user_id: str):
    users = _load_users()
    u = users.get(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    safe = dict(u)
    safe.pop("password_hash", None)
    safe["id"] = user_id
    return safe

# --------------------------------------------------------------------
# Admin: update user
# --------------------------------------------------------------------
@router.put("/{user_id}", dependencies=[Depends(require_admin)])
def update_user(user_id: str, payload: Dict[str, Any] = Body(...)):
    users = _load_users()
    u = users.get(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    # apply allowed updates (admin can set roles)
    allowed = ("firstname", "lastname", "mail", "profession", "subclasses", "is_admin", "is_moderator")
    for key in allowed:
        if key in payload:
            u[key] = payload[key]
    users[user_id] = u
    _save_users(users)
    safe = dict(u)
    safe.pop("password_hash", None)
    safe["id"] = user_id
    return safe

# --------------------------------------------------------------------
# Admin: delete user
# --------------------------------------------------------------------
@router.delete("/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: str):
    users = _load_users()
    if user_id in users:
        users.pop(user_id)
        _save_users(users)
        return {"deleted": user_id}
    raise HTTPException(status_code=404, detail="User not found")
