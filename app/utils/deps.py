# app/utils/deps.py
"""
Dépendances communes pour FastAPI (VERSION POSTGRESQL COMPLÈTE).

- get_current_user_optional : Retourne user ou None (pas d'exception)
- get_current_user_required : Lève HTTP 401 si pas authentifié
- get_current_admin : Vérifie is_admin=True
- get_current_moderator : Vérifie is_moderator=True

⚠️ NOTE: Ce fichier NE dépend PLUS de utils/json.py (supprimé)
Toutes les données viennent de PostgreSQL via SQLAlchemy.
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from utils.logger import get_logger
from utils.auth import decode_access_token
from database.connection import get_db
from models import User

logger = get_logger(__name__)


# ============================================================================
# HELPER: Récupération user depuis payload JWT
# ============================================================================

def _get_user_from_payload(db: Session, payload: Dict[str, Any]) -> Optional[User]:
    """
    Récupère un utilisateur depuis un payload JWT décodé.
    
    Args:
        db: Session SQLAlchemy
        payload: Dict JWT décodé (avec 'sub' = user_id)
    
    Returns:
        User SQLAlchemy ou None
    """
    if not payload:
        return None
    
    # Récupère user_id depuis le payload (clé 'sub' standard JWT)
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
    
    if not user_id:
        logger.debug("⚠️  Payload JWT sans user_id")
        return None
    
    # Requête PostgreSQL pour récupérer l'utilisateur
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.debug(f"⚠️  User {user_id} non trouvé en DB")
            return None
        
        return user
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération user: {e}", exc_info=True)
        return None


# ============================================================================
# DEPENDENCY: get_current_user_optional
# ============================================================================

async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """
    Tente de récupérer l'utilisateur authentifié depuis le token JWT.
    
    - Cherche le token dans Authorization header (Bearer <token>)
    - Cherche le token dans les cookies (access_token)
    - Retourne un dict avec les infos user (sans password_hash)
    - Retourne None si pas authentifié (SANS lever d'exception)
    
    Usage:
        @router.get("/")
        def index(user=Depends(get_current_user_optional)):
            if user:
                return f"Hello {user['login']}"
            return "Hello guest"
    """
    # 1. Cherche le token dans Authorization header
    auth_header = request.headers.get("authorization")
    token = None
    
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    
    # 2. Fallback: cherche dans les cookies
    if not token:
        token = request.cookies.get("access_token")
    
    # 3. Si pas de token, retourne None (mode optional)
    if not token:
        return None
    
    # 4. Décode le token JWT
    payload = decode_access_token(token)
    if not payload:
        logger.debug("⚠️  Token JWT invalide ou expiré")
        return None
    
    # 5. Récupère l'utilisateur depuis PostgreSQL
    user = _get_user_from_payload(db, payload)
    if not user:
        return None
    
    # 6. Convertit en dict (compatible avec ancien code)
    user_dict = user.to_dict()
    
    # 7. Supprime password_hash pour la sécurité
    user_dict.pop("password_hash", None)
    
    return user_dict


# ============================================================================
# DEPENDENCY: get_current_user_required
# ============================================================================

async def get_current_user_required(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retourne l'utilisateur authentifié ou lève HTTP 401.
    
    - Même logique que get_current_user_optional
    - MAIS lève HTTPException 401 si pas authentifié
    
    Usage:
        @router.get("/profile")
        def profile(user=Depends(get_current_user_required)):
            return user
    """
    user = await get_current_user_optional(request, db)
    
    if not user:
        logger.info(
            f"❌ Tentative d'accès non authentifié: "
            f"{request.client.host if request.client else 'unknown'} "
            f"→ {request.url.path}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return user


# ============================================================================
# DEPENDENCY FACTORY: require_role
# ============================================================================

def require_role(role_key: str, role_label: str):
    """
    Fabrique une dépendance qui vérifie un rôle spécifique.
    
    Args:
        role_key: Nom du champ booléen à vérifier (ex: "is_admin")
        role_label: Label pour le message d'erreur (ex: "Admin")
    
    Returns:
        Fonction dépendance utilisable avec Depends()
    
    Usage:
        require_admin = require_role("is_admin", "Admin")
        
        @router.get("/admin")
        def admin_only(user=Depends(require_admin)):
            return "Welcome admin"
    """
    async def _checker(user = Depends(get_current_user_required)):
        """Vérifie que l'utilisateur a le rôle requis."""
        # Support dict et object
        try:
            if isinstance(user, dict):
                has_role = bool(user.get(role_key))
            else:
                has_role = bool(getattr(user, role_key, False))
        except Exception:
            has_role = False
        
        if not has_role:
            logger.warning(
                f"⚠️  Accès refusé: {role_label} requis pour "
                f"user_id={user.get('id') if isinstance(user, dict) else getattr(user, 'id', None)}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role_label} privileges required"
            )
        
        return user
    
    return _checker


# ============================================================================
# DEPENDENCIES PRÉ-CONFIGURÉES
# ============================================================================

# Admin only (is_admin=True)
get_current_admin = require_role("is_admin", "Admin")

# Moderator or Admin (is_moderator=True OR is_admin=True)
async def get_current_moderator(user = Depends(get_current_user_required)):
    """Vérifie que l'utilisateur est modérateur OU admin."""
    try:
        if isinstance(user, dict):
            is_mod = bool(user.get("is_moderator") or user.get("is_admin"))
        else:
            is_mod = bool(
                getattr(user, "is_moderator", False) or 
                getattr(user, "is_admin", False)
            )
    except Exception:
        is_mod = False
    
    if not is_mod:
        logger.warning(
            f"⚠️  Accès refusé: Modérateur requis pour "
            f"user_id={user.get('id') if isinstance(user, dict) else getattr(user, 'id', None)}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator privileges required"
        )
    
    return user