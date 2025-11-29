# routes/admin_routes.py

from fastapi import APIRouter, HTTPException, Depends
from utils.roles import require_admin
from utils.json import load_json, save_json
from utils.auth import hash_password
from models.user import User
import uuid, config
from services.xp_service import add_xp
from pathlib import Path
import json

router = APIRouter(tags=["Admin"], dependencies=[Depends(require_admin)])

# helper
def load_users():
    return load_json(config.USERS_FILE)

def save_users(d):
    save_json(config.USERS_FILE, d)

# USERS CRUD (existing)
@router.get("/users")
def admin_list_users():
    return list(load_users().values())

@router.get("/users/{uid}")
def admin_get_user(uid: str):
    users = load_users()
    if uid not in users:
        raise HTTPException(404, "Utilisateur non trouvé")
    u = users[uid].copy()
    u.pop("password_hash", None)
    return u

@router.post("/users")
def admin_create_user(payload: dict):
    users = load_users()
    for u in users.values():
        if u["login"] == payload["login"]:
            raise HTTPException(400, "Login déjà utilisé")
        if u["mail"] == payload["mail"]:
            raise HTTPException(400, "Mail déjà utilisé")

    uid = str(uuid.uuid4())
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
    return {"status": "created", "id": uid}

@router.post("/users/{uid}/grant_xp")
def admin_grant_xp(uid: str, payload: dict):
    amount = int(payload.get("amount", 0))
    if amount <= 0:
        raise HTTPException(400, "amount must be > 0")
    users = load_users()
    if uid not in users:
        raise HTTPException(404)
    user = User.from_dict(users[uid])
    add_xp(user, amount)
    users[uid] = user.to_dict()
    save_users(users)
    return {"status": "ok", "xp": user.xp, "level": user.level}

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
    return _load_loot()

@router.post("/loot/tables")
def create_or_update_loot_table(payload: dict):
    # payload should be { "key": "...", "biomes":[...], "table":[...] }
    key = payload.get("key")
    if not key:
        raise HTTPException(400, "key missing")
    d = _load_loot()
    d[key] = {
        "biomes": payload.get("biomes", []),
        "table": payload.get("table", [])
    }
    _save_loot(d)
    return {"status":"saved", "key": key}

@router.delete("/loot/tables/{key}")
def delete_loot_table(key: str):
    d = _load_loot()
    if key not in d:
        raise HTTPException(404)
    del d[key]
    _save_loot(d)
    return {"status": "deleted"}
