# app/admin_api.py
"""
Chemin : app/admin_api.py

API d'administration :
- endpoints protégés par Bearer access token (JWT)
- gestion des rôles : 'admin', 'moderator', 'player'
- endpoints pour lister/éditer utilisateurs, gérer rôles, lister/révoquer devices
- vérifications d'autorisation via flags stockés dans storage/users.json (ex: is_admin, is_moderator)

Cette version est adaptée pour utiliser le système de refresh tokens
défini dans utils/auth.py et les chemins définis dans config.py.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Body
from typing import Dict, Any, Optional
from pathlib import Path
import json

import config
from utils.auth import decode_access_token, _load_refresh_store, revoke_refresh_token, revoke_all_tokens_for_user
from utils.json import load_json, save_json
# revoke_refresh_token : supprime un refresh token précis
# revoke_all_tokens_for_user : supprime tous les tokens d’un utilisateur

# ------------------------------------------------------
# Helpers storage (inchangés)
# ------------------------------------------------------

USERS_FILE = config.USERS_FILE
PROFESSIONS_FILE = config.PROFESSIONS_FILE
RECIPES_FILE = config.RECIPES_FILE
REFRESH_STORE_FILE = config.REFRESH_TOKENS_FILE

# ensure existence
for f in (USERS_FILE, PROFESSIONS_FILE, RECIPES_FILE, REFRESH_STORE_FILE):
    if not f.exists():
        save_json(f, {})

app = FastAPI(title="Admin API (roles: admin/moderator/player)")

# ------------------------------------------------------
# Auth helpers (inchangés)
# ------------------------------------------------------
def require_bearer(authorization: str = Header(...)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(401, "Authorization manquant")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "Format Authorization invalide")
    token = parts[1]
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(401, "Token invalide ou expiré")
    if payload.get("type") != "access":
        raise HTTPException(401, "Token non de type access")
    return payload

def require_player(payload: Dict[str, Any] = Depends(require_bearer)) -> Dict[str, Any]:
    users = load_json(USERS_FILE)
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id or user_id not in users:
        raise HTTPException(401, "Utilisateur inconnu")
    return users[user_id]

def require_role(role: str):
    def _checker(current_user: Dict[str, Any] = Depends(require_player)):
        if role == "admin":
            if not current_user.get("is_admin"):
                raise HTTPException(403, "Accès admin requis")
            return current_user
        if role == "moderator":
            if current_user.get("is_admin") or current_user.get("is_moderator"):
                return current_user
            raise HTTPException(403, "Accès moderator requis")
        if role == "player":
            return current_user
        raise HTTPException(500, "Role inconnu")
    return _checker

# ------------------------------------------------------
# Local helpers
# ------------------------------------------------------
def _get_all_users() -> Dict[str, Any]:
    return load_json(USERS_FILE)

def _save_all_users(data: Dict[str, Any]) -> None:
    save_json(USERS_FILE, data)

# ------------------------------------------------------
# Users management
# ------------------------------------------------------
@app.get("/admin/users", dependencies=[Depends(require_role("moderator"))])
def admin_list_users():
    users = _get_all_users()
    out = []
    for uid, u in users.items():
        out.append({
            "id": uid,
            "login": u.get("login"),
            "firstname": u.get("firstname"),
            "lastname": u.get("lastname"),
            "mail": u.get("mail"),
            "profession": u.get("profession"),
            "subclasses": u.get("subclasses", []),
            "is_admin": u.get("is_admin", False),
            "is_moderator": u.get("is_moderator", False)
        })
    return out

@app.get("/admin/users/{user_id}", dependencies=[Depends(require_role("moderator"))])
def admin_get_user(user_id: str):
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    u = users[user_id].copy()
    u.pop("password_hash", None)
    return u

@app.post("/admin/users/{user_id}/set_role", dependencies=[Depends(require_role("admin"))])
def admin_set_role(
    user_id: str,
    is_admin: Optional[bool] = Body(None),
    is_moderator: Optional[bool] = Body(None)
):
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    if is_admin is not None:
        users[user_id]["is_admin"] = bool(is_admin)
    if is_moderator is not None:
        users[user_id]["is_moderator"] = bool(is_moderator)
    _save_all_users(users)
    return {
        "status": "ok",
        "user": {
            "id": user_id,
            "is_admin": users[user_id].get("is_admin", False),
            "is_moderator": users[user_id].get("is_moderator", False)
        }
    }

@app.delete("/admin/users/{user_id}", dependencies=[Depends(require_role("admin"))])
def admin_delete_user(user_id: str):
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    users.pop(user_id)
    _save_all_users(users)
    return {"status": "deleted"}

# ------------------------------------------------------
# Moderator utility
# ------------------------------------------------------
@app.post("/admin/users/{user_id}/promote_to_moderator", dependencies=[Depends(require_role("admin"))])
def promote_to_moderator(user_id: str):
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    users[user_id]["is_moderator"] = True
    _save_all_users(users)
    return {"status": "ok"}

@app.post("/admin/users/{user_id}/demote_from_moderator", dependencies=[Depends(require_role("admin"))])
def demote_from_moderator(user_id: str):
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    users[user_id]["is_moderator"] = False
    _save_all_users(users)
    return {"status": "ok"}

# ------------------------------------------------------
# Devices / refresh tokens (adapté à utils.auth)
# ------------------------------------------------------

@app.get("/admin/users/{user_id}/devices", dependencies=[Depends(require_role("moderator"))])
def admin_list_user_devices(user_id: str):
    """
    Lister les devices (refresh tokens) d'un utilisateur.
    """
    store = _load_refresh_store()
    out = []
    for token, meta in store.items():
        if meta.get("user_id") == user_id:
            row = meta.copy()
            row["token"] = token
            out.append(row)
    return out


@app.delete("/admin/users/{user_id}/devices/{token}", dependencies=[Depends(require_role("moderator"))])
def admin_revoke_device(user_id: str, token: str):
    """
    Révoquer un refresh token particulier.
    """
    store = _load_refresh_store()
    meta = store.get(token)
    if not meta or meta.get("user_id") != user_id:
        raise HTTPException(404, "Device non trouvé")
    revoke_refresh_token(token)
    return {"status": "revoked", "token": token}


@app.delete("/admin/users/{user_id}/devices", dependencies=[Depends(require_role("admin"))])
def admin_revoke_all_user_devices(user_id: str):
    """
    Révoque tous les refresh tokens d'un utilisateur.
    """
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    revoke_all_tokens_for_user(user_id)
    return {"status": "all_revoked", "user_id": user_id}

# ------------------------------------------------------
# Bootstrap / debug
# ------------------------------------------------------
@app.post("/admin/bootstrap/make_admin/{user_id}", dependencies=[Depends(require_role("moderator"))])
def bootstrap_make_admin(user_id: str):
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    users[user_id]["is_admin"] = True
    _save_all_users(users)
    return {"status": "ok", "user_id": user_id}

@app.get("/admin/health", dependencies=[Depends(require_role("moderator"))])
def admin_health():
    return {"status": "ok", "users_count": len(load_json(USERS_FILE))}
