# app/routes/api/public/auth.py
"""
Routes d'authentification - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Body, Request, Response, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from uuid import uuid4

from config import REFRESH_TOKEN_EXPIRE_DAYS
from utils.logger import get_logger
from utils.auth import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    rotate_refresh_token,
    verify_password,
    store_refresh_token,
    revoke_refresh_token,
    revoke_all_tokens_for_user,
    get_active_devices,
)
from utils.deps import get_current_user_required
from database.connection import get_db
from models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _find_user_by_login(db: Session, login: str) -> Optional[User]:
    """Recherche un utilisateur par son login."""
    logger.debug(f"🔍 Recherche utilisateur avec login: {login}")
    
    user = db.query(User).filter(User.login == login).first()
    
    if user:
        logger.debug(f"   → Utilisateur trouvé: {user.id}")
    else:
        logger.debug(f"   → Aucun utilisateur trouvé")
    
    return user


# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------
@router.post("/login")
def login(
    payload: Dict[str, Any] = Body(...), 
    response: Response = None,
    db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur et crée une session.
    
    **Payload:**
    - login: Identifiant de l'utilisateur
    - password: Mot de passe
    - device_id: ID de l'appareil (optionnel, généré si absent)
    - device_name: Nom de l'appareil (optionnel)
    
    **Returns:**
    - access_token: Token JWT pour les requêtes API
    - device_id: ID de l'appareil (pour tracking)
    - device_name: Nom de l'appareil
    - user: Informations de l'utilisateur (sans password_hash)
    
    **Cookie:**
    - refresh_token: Token HTTP-only pour renouveler l'access_token
    """
    login_val = payload.get("login") or payload.get("username")
    password = payload.get("password")
    device_id = payload.get("device_id") or str(uuid4())
    device_name = payload.get("device_name", "")

    logger.info(f"🔐 Tentative de connexion pour: {login_val}")

    # Validation
    if not login_val or not password:
        logger.warning("⚠️  Connexion refusée: login ou mot de passe manquant")
        raise HTTPException(status_code=400, detail="Missing login or password")

    # Recherche utilisateur
    user = _find_user_by_login(db, login_val)
    if not user:
        logger.warning(f"⚠️  Échec de connexion pour {login_val}: utilisateur introuvable")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Vérification password
    logger.debug(f"   → Vérification du mot de passe pour {login_val}")
    if not verify_password(password, user.password_hash):
        logger.warning(f"⚠️  Échec de connexion pour {login_val}: mot de passe incorrect")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Création des tokens
    uid = user.id
    logger.debug(f"   → Génération des tokens pour user_id={uid}")
    
    access = create_access_token({"sub": uid})
    refresh = create_refresh_token({"sub": uid})

    # Stockage du refresh token dans PostgreSQL
    logger.debug(f"   → Stockage du refresh token pour device_id={device_id}")
    store_refresh_token(db, refresh, uid, device_id, device_name)

    # Préparation de la réponse utilisateur (sans password_hash)
    safe_user = user.to_dict()
    safe_user.pop("password_hash", None)

    # Cookie HTTP-only sécurisé
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=True,  # SSL recommandé en prod
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    logger.info(f"✅ Connexion réussie pour {login_val} (user_id={uid}, device={device_id})")

    return {
        "access_token": access,
        "device_id": device_id,
        "device_name": device_name,
        "user": safe_user,
    }


# ---------------------------------------------------------------------------
# REFRESH
# ---------------------------------------------------------------------------
@router.post("/refresh")
def refresh(
    body: Dict[str, Any] = Body(...), 
    response: Response = None,
    db: Session = Depends(get_db)
):
    """
    Renouvelle l'access_token en utilisant le refresh_token.
    
    **Rotation:** L'ancien refresh_token est révoqué et un nouveau est généré.
    
    **Payload:**
    - refresh_token: Token de rafraîchissement
    
    **Returns:**
    - access_token: Nouveau token JWT
    - refresh_token: Nouveau refresh token (l'ancien est révoqué)
    - device_id: ID de l'appareil
    """
    logger.debug("🔄 Tentative de rafraîchissement de token")
    
    old_refresh = body.get("refresh_token")
    if not old_refresh:
        logger.warning("⚠️  Rafraîchissement refusé: refresh_token manquant")
        raise HTTPException(status_code=400, detail="Missing refresh_token")

    # Vérification du token
    logger.debug("   → Vérification du refresh token")
    old_payload = decode_refresh_token(old_refresh)
    if not old_payload:
        logger.warning("⚠️  Rafraîchissement refusé: refresh token invalide")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    uid = old_payload.get("sub")
    if not uid:
        logger.error("❌ Refresh token malformé: sub manquant")
        raise HTTPException(status_code=400, detail="Malformed token")

    # Vérification que le token existe dans la DB
    from utils.auth import is_refresh_token_known
    if not is_refresh_token_known(db, old_refresh):
        logger.warning(f"⚠️  Token inconnu ou expiré pour user_id={uid}")
        raise HTTPException(status_code=401, detail="Token not found or expired")

    logger.debug(f"   → Génération de nouveaux tokens pour user_id={uid}")
    
    # Création de nouveaux tokens
    new_access = create_access_token({"sub": uid})
    new_refresh = create_refresh_token({"sub": uid})

    # Récupération du device_id depuis la DB
    from models import RefreshToken
    from utils.auth import _token_hash
    
    old_hash = _token_hash(old_refresh)
    token_entry = db.query(RefreshToken).filter(RefreshToken.token_hash == old_hash).first()
    
    device_id = token_entry.device_id if token_entry else str(uuid4())
    device_name = token_entry.device_name if token_entry else ""
    
    logger.debug(f"   → Device trouvé: {device_id}")

    # ROTATION: révoque l'ancien et stocke le nouveau
    logger.debug(f"   → Rotation du token pour device={device_id}")
    rotate_refresh_token(db, old_refresh, new_refresh, uid, device_id, device_name)

    # Cookie mis à jour
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    logger.info(f"✅ Token rafraîchi avec succès pour user_id={uid}, device={device_id}")

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "device_id": device_id,
    }


# ---------------------------------------------------------------------------
# LOGOUT (un seul device)
# ---------------------------------------------------------------------------
@router.post("/logout")
def logout(
    request: Request, 
    body: Dict[str, Any] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Déconnecte l'utilisateur sur l'appareil actuel.
    
    Révoque le refresh_token actuel (cookie ou body).
    """
    logger.info("👋 Tentative de déconnexion")
    
    # Récupère le refresh token (cookie ou body)
    refresh_token = (
        (body.get("refresh_token") if body else None)
        or request.cookies.get("refresh_token")
    )

    if refresh_token:
        try:
            logger.debug("   → Révocation du refresh token")
            revoke_refresh_token(db, refresh_token)
            logger.info("✅ Déconnexion réussie")
        except Exception as e:
            logger.warning(f"⚠️  Erreur lors de la révocation du token: {str(e)}")
    else:
        logger.debug("   → Aucun refresh token à révoquer")

    return {"message": "Logged out"}


# ---------------------------------------------------------------------------
# LOGOUT ALL (tous les devices)
# ---------------------------------------------------------------------------
@router.post("/logout_all")
def logout_all(
    user=Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Déconnecte l'utilisateur sur TOUS ses appareils.
    
    Révoque tous les refresh_tokens de l'utilisateur.
    """
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not uid:
        logger.error("❌ logout_all: user_id invalide")
        raise HTTPException(status_code=400, detail="Invalid user")
    
    logger.info(f"🔒 Révocation de toutes les sessions pour user_id={uid}")
    
    try:
        count = revoke_all_tokens_for_user(db, uid)
        logger.info(f"✅ {count} session(s) révoquée(s) pour user_id={uid}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la révocation des sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to revoke sessions")
    
    return {"message": "All sessions revoked", "count": count}


# ---------------------------------------------------------------------------
# LISTE DES DEVICES (déplacé depuis /user/me/devices)
# ---------------------------------------------------------------------------
@router.get("/devices")
def list_user_devices(
    user=Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Liste tous les appareils connectés de l'utilisateur.
    
    Retourne les refresh_tokens actifs (non expirés).
    """
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not uid:
        logger.error("❌ list_user_devices: user_id invalide")
        raise HTTPException(status_code=400, detail="Invalid user")

    logger.debug(f"📱 Liste des devices pour user_id={uid}")
    
    try:
        devices = get_active_devices(db, uid)
        logger.debug(f"   → {len(devices)} device(s) actif(s) trouvé(s)")
        return {"devices": devices}
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des devices: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve devices")


# ---------------------------------------------------------------------------
# RÉVOCATION D'UN DEVICE SPÉCIFIQUE
# ---------------------------------------------------------------------------
@router.post("/devices/{device_id}/revoke")
def revoke_device(
    device_id: str,
    user=Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Révoque un appareil spécifique de l'utilisateur.
    
    Supprime tous les refresh_tokens associés à ce device_id.
    """
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not uid:
        logger.error("❌ revoke_device: user_id invalide")
        raise HTTPException(status_code=400, detail="Invalid user")

    logger.info(f"🔒 Révocation du device {device_id} pour user_id={uid}")

    try:
        from models import RefreshToken
        
        deleted = (
            db.query(RefreshToken)
            .filter(RefreshToken.user_id == uid)
            .filter(RefreshToken.device_id == device_id)
            .delete()
        )
        
        db.commit()
        
        logger.info(f"✅ Device {device_id} révoqué avec succès ({deleted} token(s) supprimé(s))")

        return {"revoked": deleted, "device_id": device_id}
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de la révocation du device: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to revoke device")