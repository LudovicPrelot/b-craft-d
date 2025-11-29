# app/routes/admin_routes.py

from fastapi import APIRouter, HTTPException, Depends
from utils.roles import require_admin
from utils.json import load_json, save_json
from utils.auth import hash_password
from utils.logger import get_logger
from models.user import User
import uuid, config
from services.xp_service import add_xp
from pathlib import Path
import json

logger = get_logger(__name__)

router = APIRouter(tags=["Admin"], dependencies=[Depends(require_admin)])

# helper
def load_users():
    return load_json(config.USERS_FILE)

def save_users(d):
    save_json(config.USERS_FILE, d)

# USERS CRUD (existing)
@router.get("/users")
def admin_list_users():
    logger.info("👥 Admin: Liste de tous les utilisateurs")
    try:
        users = list(load_users().values())
        logger.debug(f"   → {len(users)} utilisateur(s) trouvé(s)")
        return users
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des utilisateurs", exc_info=True)
        raise HTTPException(500, "Failed to retrieve users")

@router.get("/users/{uid}")
def admin_get_user(uid: str):
    logger.info(f"👤 Admin: Récupération de l'utilisateur {uid}")
    users = load_users()
    if uid not in users:
        logger.warning(f"⚠️  Utilisateur {uid} non trouvé")
        raise HTTPException(404, "Utilisateur non trouvé")
    u = users[uid].copy()
    u.pop("password_hash", None)
    logger.debug(f"   → Utilisateur {uid} récupéré avec succès")
    return u

@router.post("/users")
def admin_create_user(payload: dict):
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

@router.post("/users/{uid}/grant_xp")
def admin_grant_xp(uid: str, payload: dict):
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

def _load_loot():
    try:
        return json.loads(config.LOOT_TABLES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_loot(d):
    config.LOOT_TABLES_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.LOOT_TABLES_FILE.write_text(json.dumps(d, indent=4, ensure_ascii=False), encoding="utf-8")

@router.get("/loot/tables")
def list_loot_tables():
    logger.info("🎲 Admin: Liste des loot tables")
    try:
        tables = _load_loot()
        logger.debug(f"   → {len(tables)} table(s) de loot trouvée(s)")
        return tables
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des loot tables", exc_info=True)
        raise HTTPException(500, "Failed to retrieve loot tables")

@router.post("/loot/tables")
def create_or_update_loot_table(payload: dict):
    key = payload.get("key")
    
    if not key:
        logger.warning("⚠️  Clé manquante pour la loot table")
        raise HTTPException(400, "key missing")
    
    logger.info(f"💾 Admin: Sauvegarde de la loot table '{key}'")
    
    try:
        d = _load_loot()
        d[key] = {
            "biomes": payload.get("biomes", []),
            "table": payload.get("table", [])
        }
        _save_loot(d)
        logger.info(f"✅ Loot table '{key}' sauvegardée avec succès")
        return {"status":"saved", "key": key}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la sauvegarde de la loot table '{key}'", exc_info=True)
        raise HTTPException(500, "Failed to save loot table")

@router.delete("/loot/tables/{key}")
def delete_loot_table(key: str):
    logger.info(f"🗑️  Admin: Suppression de la loot table '{key}'")
    
    try:
        d = _load_loot()
        if key not in d:
            logger.warning(f"⚠️  Loot table '{key}' non trouvée")
            raise HTTPException(404)
        del d[key]
        _save_loot(d)
        logger.info(f"✅ Loot table '{key}' supprimée avec succès")
        return {"status": "deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de la loot table '{key}'", exc_info=True)
        raise HTTPException(500, "Failed to delete loot table")