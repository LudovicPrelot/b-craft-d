# app/utils/deps.py
from typing import Optional
from fastapi import Request, Depends, HTTPException, status
from app.utils.auth import decode_access_token
from app.utils.json_loader import load_json
from app.config import USERS_FILE
from app.models.user import User  # on s'attend à ce que models.user définisse la classe User dataclass


def _extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract token from Authorization header (Bearer ...) or from cookie 'access_token'.
    """
    auth = request.headers.get("Authorization")
    if auth:
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
    # Fallback: cookie
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token
    return None


def get_user_from_token(token: str) -> Optional[User]:
    """
    Given a token string, decode and return a User instance (or None).
    """
    payload = decode_access_token(token)
    if not payload:
        return None
    sub = payload.get("sub")
    if not sub:
        return None

    users = load_json(USERS_FILE) or {}
    user_data = users.get(sub)
    if not user_data:
        return None

    # If models.user.User has a from_dict constructor use it; otherwise create via **dict
    try:
        if hasattr(User, "from_dict"):
            return User.from_dict(user_data)
        return User(**user_data)
    except Exception:
        # fallback: return raw dict
        return user_data


# --- FastAPI dependencies ---------------------------------------------

async def get_current_user_optional(request: Request) -> Optional[User]:
    token = _extract_token_from_request(request)
    if not token:
        return None
    return get_user_from_token(token)


async def get_current_user_required(user = Depends(get_current_user_optional)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user
