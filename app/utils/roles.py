# app/utils/roles.py
"""
Dépendances pour l'autorisation (FastAPI Depends).

Fournit :
 - require_user -> exige un utilisateur authentifié (HTTP 401 si pas auth)
 - require_role(role_key, role_label) -> fabrique une dépendance qui vérifie un flag booléen
 - require_moderator -> dépendance prête à l'emploi
 - require_admin -> dépendance prête à l'emploi

Important : pour éviter les circular imports, utils.deps est importé à l'intérieur.
"""

from fastapi import Depends, HTTPException, status
from utils.logger import get_logger

logger = get_logger(__name__)


# -------------------------
# role factory
# -------------------------
def require_role(role_key: str, role_label: str):
    """
    Fabrique une dépendance qui vérifie que l'utilisateur a le flag boolean `role_key`.
    Exemples de role_key: "is_admin", "is_moderator"
    Usage: Depends(require_role("is_admin", "Admin"))
    """

    # import local pour éviter circular import
    from utils.deps import get_current_user_required

    async def _checker(user = Depends(get_current_user_required)):
        # user may be dict or dataclass/object
        try:
            # support both dict-like and object-like
            val = None
            if isinstance(user, dict):
                val = user.get(role_key)
            else:
                val = getattr(user, role_key, None)
        except Exception:
            val = None

        if not bool(val):
            logger.warning(f"Access denied: {role_label} required for user_id={getattr(user, 'id', user.get('id') if isinstance(user, dict) else None)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role_label} privileges required"
            )
        return user

    return _checker


# -------------------------
# require_user (authentifié)
# -------------------------
def require_user():
    """
    Retourne une dépendance (callable) qui s'assure que l'utilisateur est authentifié.
    Utilise get_current_user_required() depuis utils.deps.
    Use like: Depends(require_user())
    """
    # import local pour éviter circular import au module load
    from utils.deps import get_current_user_required

    async def _dep(user = Depends(get_current_user_required)):
        # get_current_user_required doit lever 401 si non auth
        return user

    return _dep


# -------------------------
# require_moderator
# -------------------------
def require_moderator():
    """Dépendance : moderator (or admin) allowed."""
    # moderator OR admin should be allowed; implement with a small wrapper
    from utils.deps import get_current_user_required

    async def _checker(user = Depends(get_current_user_required)):
        is_mod = False
        try:
            if isinstance(user, dict):
                is_mod = bool(user.get("is_moderator") or user.get("is_admin"))
            else:
                is_mod = bool(getattr(user, "is_moderator", False) or getattr(user, "is_admin", False))
        except Exception:
            is_mod = False

        if not is_mod:
            logger.warning(f"Access denied: Moderator required for user {getattr(user, 'id', user.get('id') if isinstance(user, dict) else None)}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Moderator privileges required")
        return user

    return _checker


# -------------------------
# require_admin
# -------------------------
def require_admin():
    """Dépendance : admin only."""
    return require_role("is_admin", "Admin")