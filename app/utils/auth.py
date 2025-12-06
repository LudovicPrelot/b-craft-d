# app/utils/auth.py
"""
Utilities for password hashing and JWT-like access & refresh tokens - VERSION POSTGRESQL.

Améliorations:
 - PBKDF2-HMAC-SHA256 pour le hashing des passwords
 - JWT-like tokens signés avec HMAC-SHA256
 - Refresh tokens stockés dans PostgreSQL (table refresh_tokens)
 - Rotation: usage d'un refresh token révoque l'ancien et crée un nouveau
 - Cleanup automatique des tokens expirés
 - Support multi-device (device_id, device_name)
"""

from __future__ import annotations
import os
import json
import base64
import hashlib
import hmac
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import text

from config import (
    JWT_SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MIN,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
PBKDF2_ITERATIONS = int(os.getenv("PBKDF2_ITERATIONS", "260000"))
SALT_SIZE = int(os.getenv("PWD_SALT_SIZE", "16"))
HASH_NAME = "sha256"

# HMAC key pour hasher les refresh tokens
REFRESH_HMAC_KEY = JWT_SECRET_KEY.encode()

# ---------------------------------------------------------------------------
# Helpers: base64url
# ---------------------------------------------------------------------------
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

# ---------------------------------------------------------------------------
# Password hashing (PBKDF2-HMAC-SHA256)
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash un password avec PBKDF2-HMAC-SHA256."""
    if isinstance(password, str):
        password = password.encode("utf-8")
    salt = os.urandom(SALT_SIZE)
    dk = hashlib.pbkdf2_hmac(HASH_NAME, password, salt, PBKDF2_ITERATIONS)
    return f"pbkdf2${PBKDF2_ITERATIONS}${_b64url_encode(salt)}${_b64url_encode(dk)}"

def verify_password(password: str, hashed: str) -> bool:
    """Vérifie un password contre son hash."""
    try:
        algo, iters, salt_b64, hash_b64 = hashed.split("$")
        if algo != "pbkdf2":
            return False
        iterations = int(iters)
        salt = _b64url_decode(salt_b64)
        stored = _b64url_decode(hash_b64)
    except Exception:
        return False
    
    if isinstance(password, str):
        password = password.encode("utf-8")
    
    dk = hashlib.pbkdf2_hmac(HASH_NAME, password, salt, iterations)
    return hmac.compare_digest(dk, stored)

# ---------------------------------------------------------------------------
# JWT-like tokens (HMAC-SHA256)
# ---------------------------------------------------------------------------
ALGO = "HS256"

def _jwt_sign(message: bytes, key: bytes) -> bytes:
    """Signe un message avec HMAC-SHA256."""
    return hmac.new(key, message, hashlib.sha256).digest()

def _build_token(payload: Dict[str, Any], expires_seconds: int) -> str:
    """Construit un token JWT-like."""
    now = int(time.time())
    exp = now + expires_seconds
    header = {"alg": ALGO, "typ": "JWT"}
    payload = dict(payload)
    payload.update({"iat": now, "exp": exp})
    
    header_b = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode())
    payload_b = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    signing_input = f"{header_b}.{payload_b}".encode()
    
    sig = _jwt_sign(signing_input, JWT_SECRET_KEY.encode())
    sig_b = _b64url_encode(sig)
    
    return f"{header_b}.{payload_b}.{sig_b}"

def _decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Décode et vérifie un token JWT-like."""
    try:
        header_b, payload_b, sig_b = token.split(".")
    except Exception:
        return None
    
    try:
        signing_input = f"{header_b}.{payload_b}".encode()
        expected_sig = _jwt_sign(signing_input, JWT_SECRET_KEY.encode())
        actual_sig = _b64url_decode(sig_b)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        payload_json = _b64url_decode(payload_b)
        payload = json.loads(payload_json)
        
        if payload.get("exp", 0) < int(time.time()):
            return None
        
        return payload
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Access token
# ---------------------------------------------------------------------------
def create_access_token(data: Dict[str, Any]) -> str:
    """Crée un access token."""
    ttl = ACCESS_TOKEN_EXPIRE_MIN * 60
    return _build_token(data, ttl)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Décode un access token."""
    return _decode_token(token)

# ---------------------------------------------------------------------------
# Refresh token
# ---------------------------------------------------------------------------
def create_refresh_token(data: Dict[str, Any]) -> str:
    """Crée un refresh token."""
    ttl = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    return _build_token(data, ttl)

def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Décode un refresh token."""
    return _decode_token(token)

# ---------------------------------------------------------------------------
# Token hash (pour stockage dans DB)
# ---------------------------------------------------------------------------
def _token_hash(token: str) -> str:
    """Hash un refresh token pour le stockage."""
    if isinstance(token, str):
        token_b = token.encode("utf-8")
    else:
        token_b = token
    
    mac = hmac.new(REFRESH_HMAC_KEY, token_b, hashlib.sha256).digest()
    return _b64url_encode(mac)

# ---------------------------------------------------------------------------
# Refresh token storage (PostgreSQL)
# ---------------------------------------------------------------------------
def store_refresh_token(
    db: Session,
    token: str, 
    user_id: str, 
    device_id: str, 
    device_name: Optional[str] = None
) -> None:
    """
    Stocke un refresh token dans PostgreSQL.
    
    Args:
        db: Session SQLAlchemy
        token: Le refresh token brut
        user_id: ID de l'utilisateur
        device_id: ID de l'appareil
        device_name: Nom de l'appareil (optionnel)
    """
    from models import RefreshToken
    
    logger.debug(f"💾 Stockage refresh token pour user={user_id}, device={device_id}")
    
    # Hash le token
    th = _token_hash(token)
    
    # Décode pour extraire exp
    payload = decode_refresh_token(token) or {}
    exp_timestamp = payload.get("exp", int(time.time()) + REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    expires_at = datetime.fromtimestamp(exp_timestamp)
    
    # Crée l'entrée
    refresh_token = RefreshToken(
        token_hash=th,
        user_id=user_id,
        device_id=device_id,
        device_name=device_name or "",
        expires_at=expires_at,
    )
    
    db.add(refresh_token)
    db.commit()
    
    logger.debug(f"✅ Refresh token stocké (hash: {th[:16]}...)")


def revoke_refresh_token(db: Session, token: str) -> None:
    """
    Révoque un refresh token spécifique.
    
    Args:
        db: Session SQLAlchemy
        token: Le refresh token brut à révoquer
    """
    from models import RefreshToken
    
    th = _token_hash(token)
    logger.debug(f"🗑️  Révocation refresh token (hash: {th[:16]}...)")
    
    deleted = db.query(RefreshToken).filter(RefreshToken.token_hash == th).delete()
    db.commit()
    
    if deleted:
        logger.debug(f"✅ Token révoqué")
    else:
        logger.debug(f"⚠️  Token non trouvé (déjà révoqué?)")


def revoke_all_tokens_for_user(db: Session, user_id: str) -> int:
    """
    Révoque tous les refresh tokens d'un utilisateur.
    
    Args:
        db: Session SQLAlchemy
        user_id: ID de l'utilisateur
    
    Returns:
        Nombre de tokens révoqués
    """
    from models import RefreshToken
    
    logger.info(f"🔒 Révocation de tous les tokens pour user={user_id}")
    
    deleted = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id)
        .delete()
    )
    
    db.commit()
    
    logger.info(f"✅ {deleted} token(s) révoqué(s)")
    return deleted


def get_active_devices(db: Session, user_id: str) -> List[Dict[str, Any]]:
    """
    Retourne la liste des appareils actifs pour un utilisateur.
    
    Args:
        db: Session SQLAlchemy
        user_id: ID de l'utilisateur
    
    Returns:
        Liste de dicts avec les infos des devices
    """
    from models import RefreshToken
    
    logger.debug(f"📱 Récupération des devices actifs pour user={user_id}")
    
    # Récupère seulement les tokens non expirés
    devices = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id)
        .filter(RefreshToken.expires_at > text("NOW()"))  # ✅ Utilise text() pour SQL brut
        .all()
    )
    
    result = [
        {
            "token_hash": d.token_hash,
            "device_id": d.device_id,
            "device_name": d.device_name,
            "created_at": d.created_at.isoformat(),
            "expires_at": d.expires_at.isoformat(),
        }
        for d in devices
    ]
    
    logger.debug(f"   → {len(result)} device(s) actif(s)")
    return result


def is_refresh_token_known(db: Session, token: str) -> bool:
    """
    Vérifie si un refresh token existe dans la DB.
    
    Args:
        db: Session SQLAlchemy
        token: Le refresh token brut
    
    Returns:
        True si le token existe et n'est pas expiré
    """
    from models import RefreshToken
    
    th = _token_hash(token)
    
    exists = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == th)
        .filter(RefreshToken.expires_at > text("NOW()"))
        .first()
    )
    
    return exists is not None


def rotate_refresh_token(
    db: Session,
    old_token: str, 
    new_token: str, 
    user_id: str, 
    device_id: str, 
    device_name: Optional[str] = None
) -> None:
    """
    Rotation atomique d'un refresh token.
    
    Révoque l'ancien token et stocke le nouveau en une seule transaction.
    
    Args:
        db: Session SQLAlchemy
        old_token: Ancien refresh token à révoquer
        new_token: Nouveau refresh token à stocker
        user_id: ID de l'utilisateur
        device_id: ID de l'appareil
        device_name: Nom de l'appareil (optionnel)
    """
    from models import RefreshToken
    
    logger.debug(f"🔄 Rotation refresh token pour user={user_id}, device={device_id}")
    
    # Révoque l'ancien
    old_hash = _token_hash(old_token)
    db.query(RefreshToken).filter(RefreshToken.token_hash == old_hash).delete()
    
    # Stocke le nouveau
    new_hash = _token_hash(new_token)
    payload = decode_refresh_token(new_token) or {}
    exp_timestamp = payload.get("exp", int(time.time()) + REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    expires_at = datetime.fromtimestamp(exp_timestamp)
    
    new_refresh = RefreshToken(
        token_hash=new_hash,
        user_id=user_id,
        device_id=device_id,
        device_name=device_name or "",
        expires_at=expires_at,
    )
    
    db.add(new_refresh)
    db.commit()
    
    logger.debug(f"✅ Token rotaté avec succès")


def cleanup_expired_tokens(db: Session) -> int:
    """
    Nettoie les refresh tokens expirés de la DB.
    
    Args:
        db: Session SQLAlchemy
    
    Returns:
        Nombre de tokens supprimés
    """
    from models import RefreshToken
    
    logger.info("🧹 Nettoyage des refresh tokens expirés...")
    
    deleted = (
        db.query(RefreshToken)
        .filter(RefreshToken.expires_at <= text("NOW()"))
        .delete()
    )
    
    db.commit()
    
    logger.info(f"✅ {deleted} token(s) expiré(s) supprimé(s)")
    return deleted