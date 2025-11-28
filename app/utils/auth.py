# app/utils/auth.py
"""
Utilities for password hashing and JWT-like access tokens.
Implementation uses:
 - PBKDF2-HMAC-SHA256 for password hashing (stdlib)
 - HMAC-SHA256 for token signature (stdlib)
Tokens follow the header.payload.signature base64url pattern (compatible conceptually with JWT).
No external dependencies required.
"""

from __future__ import annotations
import os
import json
import base64
import hashlib
import hmac
import time
from typing import Optional, Dict, Any

from app.config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MIN  # must exist in config.py

# --- Password hashing (PBKDF2) ------------------------------------------------

PBKDF2_ITERATIONS = int(os.getenv("PBKDF2_ITERATIONS", "260000"))
SALT_SIZE = int(os.getenv("PWD_SALT_SIZE", "16"))  # bytes
HASH_NAME = "sha256"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    """
    Hash a password and return a string containing salt + iterations + hash in a single token.
    Format: pbkdf2$iterations$salt_b64$hash_b64
    """
    if not isinstance(password, (str, bytes)):
        raise TypeError("password must be str or bytes")
    if isinstance(password, str):
        password = password.encode("utf-8")

    salt = os.urandom(SALT_SIZE)
    dk = hashlib.pbkdf2_hmac(HASH_NAME, password, salt, PBKDF2_ITERATIONS)
    return f"pbkdf2${PBKDF2_ITERATIONS}${_b64url_encode(salt)}${_b64url_encode(dk)}"


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against the stored hash (our own format).
    """
    try:
        parts = hashed.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2":
            return False
        iterations = int(parts[1])
        salt = _b64url_decode(parts[2])
        stored = _b64url_decode(parts[3])
    except Exception:
        return False

    if isinstance(password, str):
        password = password.encode("utf-8")

    dk = hashlib.pbkdf2_hmac(HASH_NAME, password, salt, iterations)
    return hmac.compare_digest(dk, stored)


# --- Simple JWT-like tokens (HMAC-SHA256) ------------------------------------

ALGO = "HS256"


def _jwt_sign(message: bytes, key: bytes) -> bytes:
    return hmac.new(key, message, hashlib.sha256).digest()


def create_access_token(data: Dict[str, Any], expires_delta_minutes: Optional[int] = None) -> str:
    """
    Create a signed token with exp claim (minutes).
    data: payload dict (will be copied)
    returns: token string header.payload.signature (base64url)
    """
    header = {"alg": ALGO, "typ": "JWT"}
    payload = dict(data)
    now = int(time.time())
    exp = now + (expires_delta_minutes or ACCESS_TOKEN_EXPIRE_MIN or 60)
    payload.update({"iat": now, "exp": exp})

    header_b = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    payload_b = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signing_input = f"{header_b}.{payload_b}".encode("utf-8")
    sig = _jwt_sign(signing_input, JWT_SECRET_KEY.encode("utf-8"))
    sig_b = _b64url_encode(sig)
    return f"{header_b}.{payload_b}.{sig_b}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate token. Returns payload dict or None if invalid/expired.
    """
    try:
        header_b, payload_b, sig_b = token.split(".")
    except Exception:
        return None

    try:
        signing_input = f"{header_b}.{payload_b}".encode("utf-8")
        expected_sig = _jwt_sign(signing_input, JWT_SECRET_KEY.encode("utf-8"))
        actual_sig = _b64url_decode(sig_b)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload_json = _b64url_decode(payload_b)
        payload = json.loads(payload_json)
        exp = int(payload.get("exp", 0))
        if exp < int(time.time()):
            return None
        return payload
    except Exception:
        return None
