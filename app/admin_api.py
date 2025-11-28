# admin_api.py
"""
API d'administration :
- endpoints protégés par Bearer access token (JWT)
- gestion des rôles : 'admin', 'moderator', 'player'
- endpoints pour lister/éditer utilisateurs, gérer rôles, lister/revoquer devices
- vérifications d'autorisation via flags stockés dans storage/users.json (ex: is_admin, is_moderator)
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Path, Body
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

import config
from utils.auth import decode_token, _load_refresh_store, revoke_refresh_token_jti

# -------------------------
# Helpers storage
# -------------------------
def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

USERS_FILE = config.USERS_FILE
PROFESSIONS_FILE = config.PROFESSIONS_FILE
RECIPES_FILE = config.RECIPES_FILE
REFRESH_STORE_FILE = config.REFRESH_TOKENS_FILE

# ensure files exist
for f in (USERS_FILE, PROFESSIONS_FILE, RECIPES_FILE, REFRESH_STORE_FILE):
    if not f.exists():
        save_json(f, {})

app = FastAPI(title="Admin API (roles: admin/moderator/player)")

# -------------------------
# Auth helpers
# -------------------------
def require_bearer(authorization: str = Header(...)) -> Dict[str, Any]:
    """
    Validate Authorization header and return JWT payload.
    """
    if not authorization:
        raise HTTPException(401, "Authorization manquant")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "Format Authorization invalide")
    token = parts[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(401, "Token invalide ou expiré")
    if payload.get("type") != "access":
        raise HTTPException(401, "Token non de type access")
    return payload

def require_user(payload: Dict[str, Any] = Depends(require_bearer)) -> Dict[str, Any]:
    users = load_json(USERS_FILE)
    user_id = payload.get("user_id")
    if not user_id or user_id not in users:
        raise HTTPException(401, "Utilisateur inconnu")
    return users[user_id]

def require_role(role: str):
    """
    Returns a dependency that checks the current user has the given role.
    Roles considered (hierarchy):
      admin > moderator > player
    User flags: is_admin (bool), is_moderator (bool)
    """
    def _checker(current_user: Dict[str, Any] = Depends(require_user)):
        # admin passes everything
        if role == "admin":
            if not current_user.get("is_admin"):
                raise HTTPException(403, "Accès admin requis")
            return current_user
        if role == "moderator":
            if current_user.get("is_admin") or current_user.get("is_moderator"):
                return current_user
            raise HTTPException(403, "Accès moderator requis")
        if role == "player":
            # any authenticated user is at least player
            return current_user
        raise HTTPException(500, "Role inconnu")
    return _checker

# -------------------------
# Admin utilities
# -------------------------
def _get_all_users() -> Dict[str, Any]:
    return load_json(USERS_FILE)

def _save_all_users(data: Dict[str, Any]) -> None:
    save_json(USERS_FILE, data)

# -------------------------
# Endpoints : Users management
# -------------------------

@app.get("/admin/users", dependencies=[Depends(require_role("moderator"))])
def admin_list_users():
    """
    Lister tous les utilisateurs (moderator+).
    """
    users = _get_all_users()
    # return lightweight info
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
    # Do not leak password hash
    u.pop("password_hash", None)
    return u

@app.post("/admin/users/{user_id}/set_role", dependencies=[Depends(require_role("admin"))])
def admin_set_role(user_id: str, is_admin: Optional[bool] = Body(None), is_moderator: Optional[bool] = Body(None)):
    """
    Permet à un admin de définir les flags is_admin / is_moderator pour un utilisateur.
    Envoyer JSON: { "is_admin": true } ou { "is_moderator": true } ou les deux.
    """
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    if is_admin is not None:
        users[user_id]["is_admin"] = bool(is_admin)
    if is_moderator is not None:
        users[user_id]["is_moderator"] = bool(is_moderator)
    _save_all_users(users)
    return {"status": "ok", "user": {"id": user_id, "is_admin": users[user_id].get("is_admin", False), "is_moderator": users[user_id].get("is_moderator", False)}}

@app.delete("/admin/users/{user_id}", dependencies=[Depends(require_role("admin"))])
def admin_delete_user(user_id: str):
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    # Optionally revoke all refresh tokens for that user
    store = _load_refresh_store()
    to_revoke = [jti for jti, m in store.items() if m.get("user_id") == user_id]
    for jti in to_revoke:
        revoke_refresh_token_jti(jti)
    users.pop(user_id)
    _save_all_users(users)
    return {"status": "deleted"}

# -------------------------
# Endpoints : Roles self-service (for testing) 
# -------------------------
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

# -------------------------
# Devices endpoints (admin)
# -------------------------
@app.get("/admin/users/{user_id}/devices", dependencies=[Depends(require_role("moderator"))])
def admin_list_user_devices(user_id: str):
    """
    Lister les devices (refresh tokens) d'un utilisateur.
    Accessible aux moderators et admins.
    """
    store = _load_refresh_store()
    out = []
    for jti, meta in store.items():
        if meta.get("user_id") == user_id:
            entry = meta.copy()
            entry["jti"] = jti
            out.append(entry)
    return out

@app.delete("/admin/users/{user_id}/devices/{jti}", dependencies=[Depends(require_role("moderator"))])
def admin_revoke_device(user_id: str, jti: str):
    store = _load_refresh_store()
    meta = store.get(jti)
    if not meta or meta.get("user_id") != user_id:
        raise HTTPException(404, "Device non trouvé")
    revoke_refresh_token_jti(jti)
    return {"status": "revoked"}

# -------------------------
# Utility : promote current user to admin (for initial setup) - protected by moderator/admin only
# -------------------------
@app.post("/admin/bootstrap/make_admin/{user_id}", dependencies=[Depends(require_role("moderator"))])
def bootstrap_make_admin(user_id: str):
    users = _get_all_users()
    if user_id not in users:
        raise HTTPException(404, "Utilisateur introuvable")
    users[user_id]["is_admin"] = True
    _save_all_users(users)
    return {"status": "ok", "user_id": user_id}

# -------------------------
# Health / debug
# -------------------------
@app.get("/admin/health", dependencies=[Depends(require_role("moderator"))])
def admin_health():
    return {"status": "ok", "users_count": len(load_json(USERS_FILE))}
