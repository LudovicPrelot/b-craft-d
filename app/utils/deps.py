# utils/deps.py

from fastapi import Header, HTTPException, Depends
from typing import Dict, Any
from utils.auth import decode_token
from utils.storage import load_json
import config

def require_bearer(authorization: str = Header(...)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(401, "Header Authorization manquant")

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

def require_user(payload: Dict[str, Any] = Depends(require_bearer)):
    users = load_json(config.USERS_FILE)
    uid = payload.get("user_id")

    if not uid or uid not in users:
        raise HTTPException(401, "Utilisateur introuvable")

    return users[uid]
