# app/routes/admin_settings_routes.py

from fastapi import APIRouter, Depends
from utils.roles import require_admin
from utils.settings import get_settings, update_settings
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/admin/settings",
    tags=["Admin Settings"],
    dependencies=[Depends(require_admin)]
)

@router.get("/")
def read_settings():
    logger.info("⚙️  Admin: Lecture des paramètres")
    try:
        settings = get_settings()
        logger.debug(f"   → Paramètres récupérés avec succès")
        return settings
    except Exception as e:
        logger.error("❌ Erreur lors de la lecture des paramètres", exc_info=True)
        raise

@router.post("/")
def write_settings(settings: dict):
    logger.info("💾 Admin: Mise à jour des paramètres")
    logger.debug(f"   → Nouvelles valeurs: {list(settings.keys())}")
    
    try:
        update_settings(settings)
        logger.info("✅ Paramètres mis à jour avec succès")
        return {"status": "saved", "settings": settings}
    except Exception as e:
        logger.error("❌ Erreur lors de la mise à jour des paramètres", exc_info=True)
        raise