# app/routes/api/admin/settings.py
"""
Routes Admin pour les paramètres (feature flags) - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from utils.roles import require_admin
from utils.logger import get_logger
from database.connection import get_db
from models import Setting

logger = get_logger(__name__)

router = APIRouter(
    prefix="/settings", 
    tags=["Admin - Settings"], 
    dependencies=[Depends(require_admin)]
)


def _load_all_settings(db: Session) -> Dict[str, Any]:
    """Charge tous les settings depuis PostgreSQL."""
    settings = db.query(Setting).all()
    return {s.key: s.value for s in settings}


@router.get("/")
def read_settings(db: Session = Depends(get_db)):
    """
    Récupère tous les paramètres de l'application.
    
    Returns:
        Dict {key: value}
    """
    logger.info("⚙️  Admin: Lecture des paramètres")
    
    try:
        settings = _load_all_settings(db)
        logger.debug(f"   → {len(settings)} paramètre(s) récupéré(s)")
        return settings
        
    except Exception as e:
        logger.error("❌ Erreur lecture paramètres", exc_info=True)
        raise HTTPException(500, "Failed to read settings")


@router.get("/{key}")
def read_setting(
    key: str,
    db: Session = Depends(get_db)
):
    """
    Récupère un paramètre spécifique.
    
    Args:
        key: Clé du paramètre (ex: "enable_quest")
    """
    logger.info(f"⚙️  Admin: Lecture paramètre '{key}'")
    
    setting = db.query(Setting).filter(Setting.key == key).first()
    
    if not setting:
        logger.warning(f"⚠️  Paramètre '{key}' non trouvé")
        raise HTTPException(404, f"Setting '{key}' not found")
    
    return {key: setting.value}


@router.post("/")
def write_settings(
    settings: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Met à jour plusieurs paramètres.
    
    Payload: Dict {key: value}
    
    Si la clé existe, elle est mise à jour.
    Si la clé n'existe pas, elle est créée.
    """
    logger.info(f"💾 Admin: Mise à jour paramètres")
    logger.debug(f"   → Clés: {list(settings.keys())}")
    
    try:
        for key, value in settings.items():
            # Cherche si existe
            setting = db.query(Setting).filter(Setting.key == key).first()
            
            if setting:
                # Mise à jour
                setting.value = value
                logger.debug(f"   → MAJ: {key} = {value}")
            else:
                # Création
                new_setting = Setting(key=key, value=value, description="")
                db.add(new_setting)
                logger.debug(f"   → NOUVEAU: {key} = {value}")
        
        db.commit()
        
        logger.info(f"✅ {len(settings)} paramètre(s) mis à jour")
        
        return {
            "status": "saved",
            "settings": settings
        }
        
    except Exception as e:
        db.rollback()
        logger.error("❌ Erreur mise à jour paramètres", exc_info=True)
        raise HTTPException(500, "Failed to update settings")


@router.put("/{key}")
def update_setting(
    key: str,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Met à jour un paramètre spécifique.
    
    Payload:
    - value: Nouvelle valeur (peut être bool, int, str, dict, list)
    - description: Description optionnelle
    """
    value = payload.get("value")
    description = payload.get("description")
    
    if value is None:
        logger.warning("⚠️  Valeur manquante")
        raise HTTPException(400, "value is required")
    
    logger.info(f"💾 Admin: Mise à jour paramètre '{key}'")
    
    try:
        setting = db.query(Setting).filter(Setting.key == key).first()
        
        if setting:
            # Mise à jour
            setting.value = value
            if description:
                setting.description = description
            logger.debug(f"   → MAJ: {key} = {value}")
        else:
            # Création
            setting = Setting(
                key=key, 
                value=value, 
                description=description or ""
            )
            db.add(setting)
            logger.debug(f"   → NOUVEAU: {key} = {value}")
        
        db.commit()
        db.refresh(setting)
        
        logger.info(f"✅ Paramètre '{key}' sauvegardé")
        
        return {key: setting.value}
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur mise à jour paramètre '{key}'", exc_info=True)
        raise HTTPException(500, "Failed to update setting")


@router.delete("/{key}")
def delete_setting(
    key: str,
    db: Session = Depends(get_db)
):
    """Supprime un paramètre."""
    logger.info(f"🗑️  Admin: Suppression paramètre '{key}'")
    
    try:
        deleted = db.query(Setting).filter(Setting.key == key).delete()
        db.commit()
        
        if deleted == 0:
            logger.warning(f"⚠️  Paramètre '{key}' non trouvé")
            raise HTTPException(404, f"Setting '{key}' not found")
        
        logger.info(f"✅ Paramètre '{key}' supprimé")
        
        return {"deleted": key}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur suppression paramètre", exc_info=True)
        raise HTTPException(500, "Failed to delete setting")