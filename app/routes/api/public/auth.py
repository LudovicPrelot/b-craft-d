# app/routes/api/public/auth.py

from fastapi import APIRouter, Body, Request, Response, HTTPException, Depends
from typing import Dict, Any, Optional
from uuid import uuid4

from config import USERS_FILE, REFRESH_TOKENS_FILE, REFRESH_TOKEN_EXPIRE_DAYS
from utils.logger import get_logger
from utils.json import load_json, save_json
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

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialise le logger pour ce module
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _find_user_by_login(login: str) -> Optional[Dict[str, Any]]:
    """Recherche un utilisateur par son login."""
    logger.debug(f"Recherche de l'utilisateur avec login: {login}")
    users = load_json(USERS_FILE) or {}
    for uid, u in users.items():
        if u.get("login") == login:
            user = dict(u)
            user["id"] = uid
            logger.debug(f"   → Utilisateur trouvé: {uid}")
            return user
    logger.debug(f"   → Aucun utilisateur trouvé pour le login: {login}")
    return None


# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------
@router.post("/login")
def login(payload: Dict[str, Any] = Body(...), response: Response = None):
    """
    Payload: { login, password, device_id? }
    Returns { access_token, user }
    + HTTP-only cookie refresh_token
    """
    login_val = payload.get("login") or payload.get("username")
    password = payload.get("password")
    device_id = payload.get("device_id") or str(uuid4())
    device_name = payload.get("device_name") or ""  # optionnel

    logger.info(f"🔐 Tentative de connexion pour: {login_val}")

    if not login_val or not password:
        logger.warning("⚠️  Connexion refusée: login ou mot de passe manquant")
        raise HTTPException(status_code=400, detail="Missing login or password")

    user = _find_user_by_login(login_val)
    if not user:
        logger.warning(f"⚠️  Échec de connexion pour {login_val}: utilisateur introuvable")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.debug(f"   → Vérification du mot de passe pour {login_val}")
    if not verify_password(password, user.get("password_hash", "")):
        logger.warning(f"⚠️  Échec de connexion pour {login_val}: mot de passe incorrect")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens
    uid = user["id"]
    logger.debug(f"   → Génération des tokens pour user_id={uid}")
    access = create_access_token({"sub": uid})
    refresh = create_refresh_token({"sub": uid})

    # Store (HMAC-hash only)
    logger.debug(f"   → Stockage du refresh token pour device_id={device_id}")
    store_refresh_token(refresh, uid, device_id, device_name)

    # Prepare safe user
    safe_user = dict(user)
    safe_user.pop("password_hash", None)

    # Set secure cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=True,            # SSL recommended
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
# REFRESH — NOW USING rotate_refresh_token()
# ---------------------------------------------------------------------------
@router.post("/refresh")
def refresh(body: Dict[str, Any] = Body(...), response: Response = None):
    """
    Payload: { refresh_token }
    Rotate:
      - verify refresh
      - revoke old token
      - generate new tokens
      - save new refresh for same device
      - set cookie again
    """
    logger.debug("🔄 Tentative de rafraîchissement de token")
    
    old_refresh = body.get("refresh_token")
    if not old_refresh:
        logger.warning("⚠️  Rafraîchissement refusé: refresh_token manquant")
        raise HTTPException(status_code=400, detail="Missing refresh_token")

    logger.debug("   → Vérification du refresh token")
    old_payload = decode_refresh_token(old_refresh)
    if not old_payload:
        logger.warning("⚠️  Rafraîchissement refusé: refresh token invalide")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    uid = old_payload.get("sub")
    if not uid:
        logger.error("❌ Refresh token malformé: sub manquant")
        raise HTTPException(status_code=400, detail="Malformed token")

    logger.debug(f"   → Génération de nouveaux tokens pour user_id={uid}")
    
    # Create new tokens
    new_access = create_access_token({"sub": uid})
    new_refresh = create_refresh_token({"sub": uid})

    # We need device_id : get it from store via raw hashed lookup
    logger.debug("   → Recherche du device_id associé")
    devices = get_active_devices(uid)
    device_id = None
    
    for d in devices:
        from utils.auth import _token_hash
        if d["token_hash"] == _token_hash(old_refresh):
            device_id = d["device_id"]
            logger.debug(f"   → Device trouvé: {device_id}")
            break

    if not device_id:
        # fallback (rare): assign a new device_id
        device_id = str(uuid4())
        logger.warning(f"⚠️  Device non trouvé, génération d'un nouveau device_id: {device_id}")

    # ROTATE: atomic revoke + store
    logger.debug(f"   → Rotation du token pour device={device_id}")
    rotate_refresh_token(old_refresh, new_refresh, uid, device_id)

    # Set updated cookie
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
# LOGOUT — revoke only this device
# ---------------------------------------------------------------------------
@router.post("/logout")
def logout(request: Request, body: Dict[str, Any] = Body(None)):
    """
    Revoke only the current device's refresh token.
    Accepts token in body or cookie.
    """
    logger.info("👋 Tentative de déconnexion")
    
    refresh_token = (
        (body.get("refresh_token") if body else None)
        or request.cookies.get("refresh_token")
    )

    if refresh_token:
        try:
            logger.debug("   → Révocation du refresh token")
            revoke_refresh_token(refresh_token)
            logger.info("✅ Déconnexion réussie")
        except Exception as e:
            logger.warning(f"⚠️  Erreur lors de la révocation du token: {str(e)}")
    else:
        logger.debug("   → Aucun refresh token à révoquer")

    return {"message": "Logged out"}


# ---------------------------------------------------------------------------
# LOGOUT ALL — revoke all sessions of user
# ---------------------------------------------------------------------------
@router.post("/logout_all")
def logout_all(user = Depends(get_current_user_required)):
    """Révoque toutes les sessions d'un utilisateur."""
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not uid:
        logger.error("❌ logout_all: user_id invalide")
        raise HTTPException(status_code=400, detail="Invalid user")
    
    logger.info(f"🔒 Révocation de toutes les sessions pour user_id={uid}")
    
    try:
        revoke_all_tokens_for_user(uid)
        logger.info(f"✅ Toutes les sessions révoquées pour user_id={uid}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la révocation des sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to revoke sessions")
    
    return {"message": "All sessions revoked"}
