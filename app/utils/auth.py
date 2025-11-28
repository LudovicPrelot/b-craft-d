from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import uuid
import json

from pathlib import Path
import config  # <— NEW: centralised env & paths

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _load_refresh_store() -> Dict[str, Any]:
    if not config.REFRESH_TOKENS_FILE.exists():
        return {}
    try:
        return json.loads(config.REFRESH_TOKENS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_refresh_store(data: Dict[str, Any]) -> None:
    config.REFRESH_TOKENS_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.REFRESH_TOKENS_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8"
    )


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        return False


def create_access_token(subject: Dict[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MIN)
    payload = {
        **subject,
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def create_refresh_token(subject: Dict[str, Any], device_info=None) -> str:
    jti = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        **subject,
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "jti": jti
    }

    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    # store metadata for multi-device
    store = _load_refresh_store()
    store[jti] = {
        "user_id": subject.get("user_id"),
        "device_id": device_info.get("device_id") if device_info else None,
        "user_agent": device_info.get("user_agent") if device_info else None,
        "ip": device_info.get("ip") if device_info else None,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expire.isoformat(),
    }

    _save_refresh_store(store)
    return token


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except JWTError:
        raise ValueError("Token invalide")


def validate_refresh_token(token: str) -> Dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise ValueError("Mauvais type de token (refresh attendu)")
    jti = payload.get("jti")
    if not jti:
        raise ValueError("Token refresh sans JTI")

    store = _load_refresh_store()
    if jti not in store:
        raise ValueError("Refresh token révoqué ou inconnu")

    return payload


def revoke_refresh_token_jti(jti: str):
    store = _load_refresh_store()
    if jti in store:
        del store[jti]
        _save_refresh_store(store)


def rotate_refresh_token(old_token: str, subject: Dict[str, Any], device_info=None):
    payload = decode_token(old_token)
    if "jti" in payload:
        revoke_refresh_token_jti(payload["jti"])
    return create_refresh_token(subject, device_info)
