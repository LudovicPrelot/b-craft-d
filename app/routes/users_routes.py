# routes/users_routes.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from utils.roles import require_role_admin, require_role_moderator
from utils.deps import require_user
from utils.auth import hash_password
from utils.storage import load_json, save_json
from models.user import User
import config

router = APIRouter(tags=["Users"])


@router.get("/me")
def me_route(current=Depends(require_user)):
    u = User.from_dict(current)
    data = u.to_dict()
    data.pop("password_hash", None)
    return data


@router.get("/users", dependencies=[Depends(require_role_admin)])
def list_users():
    return list(load_json(config.USERS_FILE).values())


@router.get("/users/{uid}", dependencies=[Depends(require_role_moderator)])
def get_user(uid: str):
    data = load_json(config.USERS_FILE)
    if uid not in data:
        raise HTTPException(404)
    u = data[uid].copy()
    u.pop("password_hash", None)
    return u


@router.put("/users/{uid}", dependencies=[Depends(require_role_moderator)])
def update_user(uid: str, payload: Dict[str, Any]):
    data = load_json(config.USERS_FILE)
    if uid not in data:
        raise HTTPException(404)

    user = data[uid]

    for k, v in payload.items():
        if k == "password":
            user["password_hash"] = hash_password(v)
        else:
            user[k] = v

    data[uid] = user
    save_json(config.USERS_FILE, data)

    user.pop("password_hash", None)
    return user
