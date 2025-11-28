# utils/roles.py

from fastapi import HTTPException, Depends
from utils.deps import require_user

def require_role_admin(user=Depends(require_user)):
    if not user.get("is_admin"):
        raise HTTPException(403, "Action réservée aux administrateurs")
    return user

def require_role_moderator(user=Depends(require_user)):
    if not (user.get("is_admin") or user.get("is_moderator")):
        raise HTTPException(403, "Action réservée aux modérateurs")
    return user

def require_role_player(user=Depends(require_user)):
    # Toute personne loggée est au moins joueur
    return user
