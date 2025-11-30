# app/routes/api/admin/users.py

from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Any, Dict
from utils.roles import require_admin
from utils.json import load_users, save_users
from utils.auth import hash_password
from utils.logger import get_logger
from models.user import User
import uuid
from services.xp_service import add_xp

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Admin - Users"], dependencies=[Depends(require_admin)])

@router.get("/", dependencies=[Depends(require_admin)])
def list_users():
    logger.info("👥 Admin: Liste de tous les utilisateurs")
    try:
        users = list(load_users().values())
        logger.debug(f"   → {len(users)} utilisateur(s) trouvé(s)")
        return users
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des utilisateurs", exc_info=True)
        raise HTTPException(500, "Failed to retrieve users")

@router.post("/create", dependencies=[Depends(require_admin)], status_code=201)
def create_user(payload: dict):
    logger.info(f"➕ Admin: Création d'un nouvel utilisateur (login: {payload.get('login')})")
    
    users = load_users()
    
    # Vérification login unique
    for u in users.values():
        if u["login"] == payload["login"]:
            logger.warning(f"⚠️  Login {payload['login']} déjà utilisé")
            raise HTTPException(400, "Login déjà utilisé")
        if u["mail"] == payload["mail"]:
            logger.warning(f"⚠️  Mail {payload['mail']} déjà utilisé")
            raise HTTPException(400, "Mail déjà utilisé")

    uid = str(uuid.uuid4())
    logger.debug(f"   → Génération de l'ID utilisateur: {uid}")
    
    try:
        user = User(
            id=uid,
            firstname=payload["firstname"],
            lastname=payload["lastname"],
            mail=payload["mail"],
            login=payload["login"],
            password_hash=hash_password(payload["password"]),
            profession=payload.get("profession", ""),
            subclasses=payload.get("subclasses", []),
            inventory=payload.get("inventory", {}),
            xp=payload.get("xp", 0),
            level=payload.get("level", 1),
            stats=payload.get("stats", {"strength":1,"agility":1,"endurance":1}),
            biome=payload.get("biome",""),
            is_admin=payload.get("is_admin", False),
            is_moderator=payload.get("is_moderator", False)
        )
        users[uid] = user.to_dict()
        save_users(users)
        
        logger.info(f"✅ Utilisateur {payload['login']} créé avec succès (id: {uid})")
        return {"status": "created", "id": uid}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de l'utilisateur", exc_info=True)
        raise HTTPException(500, "Failed to create user")

@router.get("/{uid}", dependencies=[Depends(require_admin)])
def get_user(uid: str):
    logger.info(f"👤 Admin: Récupération de l'utilisateur {uid}")
    users = load_users()
    if uid not in users:
        logger.warning(f"⚠️  Utilisateur {uid} non trouvé")
        raise HTTPException(404, "Utilisateur non trouvé")
    u = users[uid].copy()
    u.pop("password_hash", None)
    logger.debug(f"   → Utilisateur {uid} récupéré avec succès")
    return u

@router.put("/{uid}", dependencies=[Depends(require_admin)])
def update_user(uid: str, payload: Dict[str, Any] = Body(...)):
    logger.info(f"✏️  Admin: Mise à jour de l'utilisateur {uid}")
    logger.debug(f"   → Champs à mettre à jour: {list(payload.keys())}")
    
    try:
        users = load_users()
        u = users.get(uid)
        if not u:
            logger.warning(f"⚠️  Utilisateur {uid} non trouvé")
            raise HTTPException(status_code=404, detail="User not found")
        
        # apply allowed updates (admin can set roles)
        allowed = ("firstname", "lastname", "mail", "profession", "subclasses", "is_admin", "is_moderator")
        for key in allowed:
            if key in payload:
                u[key] = payload[key]
        
        users[uid] = u
        save_users(users)
        
        safe = dict(u)
        safe.pop("password_hash", None)
        safe["id"] = uid
        
        logger.info(f"✅ Utilisateur {uid} mis à jour avec succès")
        return safe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour de l'utilisateur {uid}", exc_info=True)
        raise HTTPException(500, "Failed to update user")

@router.delete("/{uid}", dependencies=[Depends(require_admin)])
def delete_user(uid: str):
    logger.info(f"🗑️  Admin: Suppression de l'utilisateur {uid}")
    
    try:
        users = load_users()
        if uid in users:
            users.pop(uid)
            save_users(users)
            logger.info(f"✅ Utilisateur {uid} supprimé avec succès")
            return {"deleted": uid}
        
        logger.warning(f"⚠️  Utilisateur {uid} non trouvé")
        raise HTTPException(status_code=404, detail="User not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de l'utilisateur {uid}", exc_info=True)
        raise HTTPException(500, "Failed to delete user")

@router.post("/{uid}/grant_xp", dependencies=[Depends(require_admin)])
def grant_xp(uid: str, payload: dict):
    amount = int(payload.get("amount", 0))
    logger.info(f"⭐ Admin: Ajout de {amount} XP à l'utilisateur {uid}")
    
    if amount <= 0:
        logger.warning(f"⚠️  Montant invalide: {amount}")
        raise HTTPException(400, "amount must be > 0")
        
    users = load_users()
    if uid not in users:
        logger.warning(f"⚠️  Utilisateur {uid} non trouvé")
        raise HTTPException(404)
        
    try:
        user = User.from_dict(users[uid])
        old_level = user.level
        add_xp(user, amount)
        users[uid] = user.to_dict()
        save_users(users)
        
        if user.level > old_level:
            logger.info(f"✅ XP ajoutée et level up! {old_level} → {user.level} (XP: {user.xp})")
        else:
            logger.info(f"✅ {amount} XP ajoutée (niveau: {user.level}, XP: {user.xp})")
            
        return {"status": "ok", "xp": user.xp, "level": user.level}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout d'XP", exc_info=True)
        raise HTTPException(500, "Failed to grant XP")