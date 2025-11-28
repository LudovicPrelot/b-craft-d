# app/utils/roles.py
from fastapi import Depends, HTTPException, status
from app.utils.deps import get_current_user_required
from typing import Any

# user can be dataclass User or dict depending on models
def _is_admin(user: Any) -> bool:
    try:
        return bool(getattr(user, "is_admin", None) or user.get("is_admin", False))
    except Exception:
        return False

def _is_moderator(user: Any) -> bool:
    try:
        return bool(getattr(user, "is_moderator", None) or user.get("is_moderator", False))
    except Exception:
        return False

def require_admin(user = Depends(get_current_user_required)):
    if not _is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user

def require_moderator(user = Depends(get_current_user_required)):
    if not (_is_admin(user) or _is_moderator(user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Moderator privileges required")
    return user

def require_player(user = Depends(get_current_user_required)):
    # any authenticated user
    return user
