# routes/auth_routes.py

from fastapi import APIRouter, HTTPException, Body, Request
from typing import Dict, Any
import uuid
import config

from utils.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, validate_refresh_token,
    rotate_refresh_token, revoke_refresh_token_jti
)
from utils.storage import load_json, save_json
from models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(data: Dict[str, Any]):
    users_raw = load_json(config.USERS_FILE)

    for u in users_raw.values():
        if u["login"] == data["login"]:
            raise HTTPException(400, "Login déjà utilisé")
        if u["mail"] == data["mail"]:
            raise HTTPException(400, "Mail déjà utilisé")

    uid = str(uuid.uuid4())
    user = User(
        id=uid,
        firstname=data["firstname"],
        lastname=data["lastname"],
        mail=data["mail"],
        login=data["login"],
        password_hash=hash_password(data["password"]),
        profession=data.get("profession", ""),
        subclasses=data.get("subclasses", []),
        inventory={},             # <-- IMPORTANT
        is_admin=False,
        is_moderator=False
    )

    users_raw[uid] = user.to_dict()
    save_json(config.USERS_FILE, users_raw)

    return {"status": "registered", "user_id": uid}


@router.post("/login")
def login(payload: Dict[str, Any], request: Request):
    users = load_json(config.USERS_FILE)

    user_data = next((u for u in users.values() if u["login"] == payload["login"]), None)
    if not user_data:
        raise HTTPException(401, "Identifiants invalides")

    user = User.from_dict(user_data)

    if not verify_password(payload["password"], user.password_hash):
        raise HTTPException(401, "Identifiants invalides")

    subject = {"user_id": user.id}

    access = create_access_token(subject)
    refresh = create_refresh_token(subject)

    return {"access_token": access, "refresh_token": refresh}


@router.post("/refresh")
def refresh(refresh_token: str = Body(..., embed=True)):
    payload = validate_refresh_token(refresh_token)
    uid = payload["user_id"]

    return {
        "access_token": create_access_token({"user_id": uid}),
        "refresh_token": rotate_refresh_token(refresh_token, {"user_id": uid})
    }


@router.post("/logout")
def logout(refresh_token: str = Body(..., embed=True)):
    payload = decode_token(refresh_token)
    revoke_refresh_token_jti(payload["jti"])
    return {"status": "logged_out"}
