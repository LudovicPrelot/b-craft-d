# app/routes/api/public/professions.py
from fastapi import APIRouter, HTTPException
from utils.json import load_json
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Professions"])

@router.get("")
def list_professions():
    logger.info("🌍 Accès public: Liste des professions")
    try:
        professions = load_json(config.PROFESSIONS_FILE)
        logger.debug(f"   → {len(professions)} profession(s) disponible(s)")
        return {"professions": list(professions.values())}
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des professions", exc_info=True)
        raise HTTPException(500, "Failed to retrieve professions")