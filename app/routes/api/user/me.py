# app/routes/api/user/me.py

from fastapi import APIRouter, Depends, HTTPException
from utils.logger import get_logger
from utils.deps import get_current_user_required
from utils.auth import get_active_devices
from utils.json import load_json, save_json
from config import REFRESH_TOKENS_FILE

logger = get_logger(__name__)

router = APIRouter(prefix="/me", tags=["Users - Profile"], dependencies=[Depends(get_current_user_required)])

# --------------------------------------------------------------------
# PROFILE
# --------------------------------------------------------------------
@router.get("/")
def me(user = Depends(get_current_user_required)):
    """
    Return current user info (without password_hash).
    """
    user_id = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    logger.debug(f"👤 Récupération du profil pour user_id={user_id}")
    
    # user can be dict or dataclass
    if isinstance(user, dict):
        safe = dict(user)
        safe.pop("password_hash", None)
        return safe
    # dataclass-like fallback
    try:
        return {
            "id": getattr(user, "id", None),
            "firstname": getattr(user, "firstname", ""),
            "lastname": getattr(user, "lastname", ""),
            "mail": getattr(user, "mail", ""),
            "login": getattr(user, "login", "")
        }
    except Exception:
        return {}

# ---------------------------------------------------------------------------
# DEVICE LIST
# ---------------------------------------------------------------------------
@router.get("/devices")
def list_devices(user = Depends(get_current_user_required)):
    """Liste tous les appareils connectés de l'utilisateur."""
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not uid:
        logger.error("❌ list_devices: user_id invalide")
        raise HTTPException(status_code=400, detail="Invalid user")

    logger.debug(f"📱 Liste des devices pour user_id={uid}")
    
    try:
        devices = get_active_devices(uid)
        logger.debug(f"   → {len(devices)} device(s) actif(s) trouvé(s)")
        return {"devices": devices}
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des devices: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve devices")


# ---------------------------------------------------------------------------
# DEVICE REVOKE
# ---------------------------------------------------------------------------
@router.post("/devices/{device_id}/revoke")
def revoke_device(device_id: str, user = Depends(get_current_user_required)):
    """Révoque un appareil spécifique."""
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not uid:
        logger.error("❌ revoke_device: user_id invalide")
        raise HTTPException(status_code=400, detail="Invalid user")

    logger.info(f"🔒 Révocation du device {device_id} pour user_id={uid}")

    try:
        # Remove tokens matching the device (hashed store)
        store = load_json(REFRESH_TOKENS_FILE) or {}
        to_delete = []

        # Need to check hashed entries
        for token_hash, meta in store.items():
            if meta.get("user_id") == uid and meta.get("device_id") == device_id:
                to_delete.append(token_hash)

        logger.debug(f"   → {len(to_delete)} token(s) à supprimer")
        
        for th in to_delete:
            store.pop(th, None)

        save_json(REFRESH_TOKENS_FILE, store)

        logger.info(f"✅ Device {device_id} révoqué avec succès ({len(to_delete)} token(s) supprimé(s))")

        return {"revoked": len(to_delete)}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la révocation du device: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to revoke device")