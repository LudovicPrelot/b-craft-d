# app/utils/auth.py
"""
Chemin : app/utils/auth.py

Utilities for password hashing and JWT-like access & refresh tokens.
Improvements:
 - PBKDF2-HMAC-SHA256 for password hashing
 - JWT-like tokens signed with HMAC-SHA256
 - Refresh tokens are stored hashed in REFRESH_TOKENS_FILE (HMAC with JWT_SECRET_KEY)
 - Rotation: refresh usage revokes old token and issues a new one
 - Cleanup: expired tokens removed from store on access
 - Multi-device support (device_id, optional device_name)
 - Public API:
     hash_password, verify_password,
     create_access_token, decode_access_token,
     create_refresh_token, decode_refresh_token,
     store_refresh_token, revoke_refresh_token,
     revoke_all_tokens_for_user, get_active_devices, revoke_device_token
"""

from __future__ import annotations
import os
import json
import base64
import hashlib
import hmac
import time
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv

from config import (
    JWT_SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MIN,
    REFRESH_TOKEN_EXPIRE_DAYS,
    REFRESH_TOKENS_FILE,
)

load_dotenv()  # reads variables from a .env file and sets them in os.environ

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
PBKDF2_ITERATIONS = int(os.getenv("PBKDF2_ITERATIONS", "260000"))
SALT_SIZE = int(os.getenv("PWD_SALT_SIZE", "16"))
HASH_NAME = "sha256"

# How we hash refresh tokens for storage (HMAC with secret)
REFRESH_HMAC_KEY = JWT_SECRET_KEY.encode()  # reuse secret for HMAC of tokens

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
    if isinstance(password, str):
        password = password.encode("utf-8")
    salt = os.urandom(SALT_SIZE)
    dk = hashlib.pbkdf2_hmac(HASH_NAME, password, salt, PBKDF2_ITERATIONS)
    return f"pbkdf2${PBKDF2_ITERATIONS}${_b64url_encode(salt)}${_b64url_encode(dk)}"

def verify_password(password: str, hashed: str) -> bool:
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
    # single HMAC is acceptable; we can add key stretching if needed
    return hmac.new(key, message, hashlib.sha256).digest()

def _build_token(payload: Dict[str, Any], expires_seconds: int) -> str:
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
# Access token helpers
# ---------------------------------------------------------------------------
def create_access_token(data: Dict[str, Any]) -> str:
    ttl = ACCESS_TOKEN_EXPIRE_MIN * 60
    return _build_token(data, ttl)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    return _decode_token(token)

# ---------------------------------------------------------------------------
# Refresh token helpers
# ---------------------------------------------------------------------------
def create_refresh_token(data: Dict[str, Any]) -> str:
    ttl = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    return _build_token(data, ttl)

def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    return _decode_token(token)

# ---------------------------------------------------------------------------
# Refresh token storage (hashed keys)
# Format stored: { "<token_hmac>": { "user_id":..., "device_id":..., "created_at":..., "exp": ... } }
# ---------------------------------------------------------------------------
def _ensure_store_dir():
    d = os.path.dirname(REFRESH_TOKENS_FILE)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def _load_refresh_store_raw() -> Dict[str, Any]:
    """
    Load raw store file (may contain hashed keys).
    """
    if not os.path.exists(REFRESH_TOKENS_FILE):
        return {}
    try:
        with open(REFRESH_TOKENS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _save_refresh_store_raw(store: Dict[str, Any]) -> None:
    _ensure_store_dir()
    with open(REFRESH_TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=4)

def _token_hash(token: str) -> str:
    """
    Deterministic hash (HMAC) of the refresh token used as key in store.
    """
    if isinstance(token, str):
        token_b = token.encode("utf-8")
    else:
        token_b = token
    mac = hmac.new(REFRESH_HMAC_KEY, token_b, hashlib.sha256).digest()
    return _b64url_encode(mac)

def _cleanup_expired(store: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove entries whose exp < now from store.
    """
    now = int(time.time())
    to_del = []
    for key, meta in store.items():
        exp = meta.get("exp")
        if exp is None:
            # if exp missing, keep (backwards compatibility) or remove? we remove to be safe
            to_del.append(key)
        else:
            if exp < now:
                to_del.append(key)
    for k in to_del:
        store.pop(k, None)
    return store

# Public store functions ----------------------------------------------------
def store_refresh_token(token: str, user_id: str, device_id: str, device_name: Optional[str] = None) -> None:
    """
    Store a refresh token in the store under its HMAC key.
    We also store 'exp' (expiration) to allow cleanup.
    """
    raw = _load_refresh_store_raw()
    raw = _cleanup_expired(raw)
    th = _token_hash(token)
    # decode token to extract exp (if possible)
    payload = decode_refresh_token(token) or {}
    exp = payload.get("exp", int(time.time()) + REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    meta = {
        "user_id": user_id,
        "device_id": device_id,
        "device_name": device_name or "",
        "created_at": int(time.time()),
        "exp": int(exp)
    }
    raw[th] = meta
    _save_refresh_store_raw(raw)

def revoke_refresh_token(token: str) -> None:
    """
    Revoke a specific refresh token by computing its hash and deleting the entry.
    """
    raw = _load_refresh_store_raw()
    th = _token_hash(token)
    if th in raw:
        raw.pop(th, None)
        _save_refresh_store_raw(raw)

def revoke_all_tokens_for_user(user_id: str) -> None:
    raw = _load_refresh_store_raw()
    raw = _cleanup_expired(raw)
    new = {k: v for k, v in raw.items() if v.get("user_id") != user_id}
    _save_refresh_store_raw(new)

def get_active_devices(user_id: str) -> List[Dict[str, Any]]:
    """
    Return list of devices for a user.
    Each entry: { "token_hash": "<h>", "device_id": "...", "device_name": "...", "created_at": ..., "exp": ... }
    Note: we don't expose raw tokens here.
    """
    raw = _load_refresh_store_raw()
    raw = _cleanup_expired(raw)
    out = []
    for th, meta in raw.items():
        if meta.get("user_id") == user_id:
            item = {
                "token_hash": th,
                "device_id": meta.get("device_id"),
                "device_name": meta.get("device_name", ""),
                "created_at": meta.get("created_at"),
                "exp": meta.get("exp")
            }
            out.append(item)
    return out

def revoke_device_token(device_token: str) -> None:
    """
    Alias to revoke_refresh_token()
    """
    revoke_refresh_token(device_token)

# Utility to check if a provided refresh token is known (by hashing)
def is_refresh_token_known(token: str) -> bool:
    raw = _load_refresh_store_raw()
    raw = _cleanup_expired(raw)
    th = _token_hash(token)
    return th in raw

# Rotate helper: revoke old token and store new token (atomic)
def rotate_refresh_token(old_token: str, new_token: str, user_id: str, device_id: str, device_name: Optional[str] = None) -> None:
    """
    Revoke old_token and store new_token for same user/device.
    """
    raw = _load_refresh_store_raw()
    raw = _cleanup_expired(raw)
    old_h = _token_hash(old_token)
    if old_h in raw:
        raw.pop(old_h, None)
    # store new
    new_h = _token_hash(new_token)
    payload = decode_refresh_token(new_token) or {}
    exp = payload.get("exp", int(time.time()) + REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    raw[new_h] = {
        "user_id": user_id,
        "device_id": device_id,
        "device_name": device_name or "",
        "created_at": int(time.time()),
        "exp": int(exp)
    }
    _save_refresh_store_raw(raw)
