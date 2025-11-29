# app/routes/users_routes.py

from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict, Any, Optional
from uuid import uuid4

import config
from utils.json import load_json, save_json
from utils.auth import hash_password
from utils.deps import get_current_user_required
from utils.roles import require_admin
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/users", tags=["Users"])

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
    
    logger.info(f"📝 Inscription d'un nouvel utilisateur: {login}")

    if not login or not password:
        logger.warning("⚠️  Inscription refusée: login ou password manquant")
        raise HTTPException(status_code=400, detail="login and password required")

    users = _load_users()

    # ensure unique login
    for uid, u in users.items():
        if u.get("login") == login:
            logger.warning(f"⚠️  Inscription refusée: login '{login}' déjà utilisé")
            raise HTTPException(status_code=400, detail="login already exists")

    uid = str(uuid4())
    logger.debug(f"   → Génération de l'ID utilisateur: {uid}")
    
    try:
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
        
        logger.info(f"✅ Utilisateur '{login}' créé avec succès (id: {uid})")
        return {"id": uid, "user": safe}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de l'utilisateur '{login}'", exc_info=True)
        raise HTTPException(500, "Failed to create user")

# --------------------------------------------------------------------
# Current user
# --------------------------------------------------------------------
@router.get("/me")
def me(user = Depends(get_current_user_required)):
    """
    Return current user info (without password_hash).
    """
    user_id = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    logger.debug(f"👤 Récupération du profil pour user_id={user_id}")
    
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
    logger.info("👥 Admin: Liste de tous les utilisateurs")
    
    try:
        users = _load_users()
        out = []
        for uid, u in users.items():
            safe = dict(u)
            safe.pop("password_hash", None)
            safe["id"] = uid
            out.append(safe)
        
        logger.debug(f"   → {len(out)} utilisateur(s) trouvé(s)")
        return out
        
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des utilisateurs", exc_info=True)
        raise HTTPException(500, "Failed to retrieve users")

# --------------------------------------------------------------------
# Admin: get user
# --------------------------------------------------------------------
@router.get("/{user_id}", dependencies=[Depends(require_admin)])
def get_user(user_id: str):
    logger.info(f"👤 Admin: Récupération de l'utilisateur {user_id}")
    
    try:
        users = _load_users()
        u = users.get(user_id)
        if not u:
            logger.warning(f"⚠️  Utilisateur {user_id} non trouvé")
            raise HTTPException(status_code=404, detail="User not found")
        
        safe = dict(u)
        safe.pop("password_hash", None)
        safe["id"] = user_id
        
        logger.debug(f"   → Utilisateur {user_id} récupéré")
        return safe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération de l'utilisateur {user_id}", exc_info=True)
        raise HTTPException(500, "Failed to retrieve user")

# --------------------------------------------------------------------
# Admin: update user
# --------------------------------------------------------------------
@router.put("/{user_id}", dependencies=[Depends(require_admin)])
def update_user(user_id: str, payload: Dict[str, Any] = Body(...)):
    logger.info(f"✏️  Admin: Mise à jour de l'utilisateur {user_id}")
    logger.debug(f"   → Champs à mettre à jour: {list(payload.keys())}")
    
    try:
        users = _load_users()
        u = users.get(user_id)
        if not u:
            logger.warning(f"⚠️  Utilisateur {user_id} non trouvé")
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
        
        logger.info(f"✅ Utilisateur {user_id} mis à jour avec succès")
        return safe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour de l'utilisateur {user_id}", exc_info=True)
        raise HTTPException(500, "Failed to update user")

# --------------------------------------------------------------------
# Admin: delete user
# --------------------------------------------------------------------
@router.delete("/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: str):
    logger.info(f"🗑️  Admin: Suppression de l'utilisateur {user_id}")
    
    try:
        users = _load_users()
        if user_id in users:
            users.pop(user_id)
            _save_users(users)
            logger.info(f"✅ Utilisateur {user_id} supprimé avec succès")
            return {"deleted": user_id}
        
        logger.warning(f"⚠️  Utilisateur {user_id} non trouvé")
        raise HTTPException(status_code=404, detail="User not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de l'utilisateur {user_id}", exc_info=True)
        raise HTTPException(500, "Failed to delete user")