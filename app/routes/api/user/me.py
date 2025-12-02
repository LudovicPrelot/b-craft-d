# app/routes/api/user/me.py
"""
Routes user pour le profil utilisateur.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils.logger import get_logger
from utils.deps import get_current_user_required
from database.connection import get_db
from models import User, RefreshToken
from schemas.user import UserResponse
from sqlalchemy import text

logger = get_logger(__name__)

router = APIRouter(prefix="/me", tags=["Users - Profile"], dependencies=[Depends(get_current_user_required)])


@router.get("/", response_model=UserResponse)
def get_profile(
    user=Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Récupère le profil complet de l'utilisateur connecté.
    """
    user_id = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    logger.debug(f"👤 Récupération du profil pour user_id={user_id}")
    
    # Récupère l'utilisateur depuis la DB pour avoir les données à jour
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(404, "User not found")
    
    return db_user


@router.get("/devices")
def list_devices(
    user=Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Liste tous les appareils connectés de l'utilisateur."""
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not uid:
        logger.error("❌ list_devices: user_id invalide")
        raise HTTPException(status_code=400, detail="Invalid user")

    logger.debug(f"📱 Liste des devices pour user_id={uid}")
    
    try:
        devices = (
            db.query(RefreshToken)
            .filter(RefreshToken.user_id == uid)
            .filter(RefreshToken.expires_at > text("NOW()"))  # ✅ Utilise text() pour SQL brut
            .all()
        )
        
        result = [
            {
                "token_hash": d.token_hash,
                "device_id": d.device_id,
                "device_name": d.device_name,
                "created_at": d.created_at.isoformat(),
                "expires_at": d.expires_at.isoformat(),
            }
            for d in devices
        ]
        
        logger.debug(f"   → {len(result)} device(s) actif(s) trouvé(s)")
        return {"devices": result}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des devices: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve devices")


@router.post("/devices/{device_id}/revoke")
def revoke_device(
    device_id: str,
    user=Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Révoque un appareil spécifique."""
    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not uid:
        logger.error("❌ revoke_device: user_id invalide")
        raise HTTPException(status_code=400, detail="Invalid user")

    logger.info(f"🔒 Révocation du device {device_id} pour user_id={uid}")

    try:
        deleted = (
            db.query(RefreshToken)
            .filter(RefreshToken.user_id == uid)
            .filter(RefreshToken.device_id == device_id)
            .delete()
        )
        
        db.commit()
        
        logger.info(f"✅ Device {device_id} révoqué avec succès ({deleted} token(s) supprimé(s))")

        return {"revoked": deleted}
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de la révocation du device: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to revoke device")