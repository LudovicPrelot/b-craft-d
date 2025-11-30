# app/routes/api/public/resources.py
from fastapi import APIRouter, HTTPException
from utils.json import load_json
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Resources"])

@router.get("/")
def list_ingredients():
    logger.info("🌍 Accès public: Liste des ressources")
    try:
        resources = load_json(config.RESOURCES_FILE)
        logger.debug(f"   → {len(resources)} ressource(s) disponible(s)")
        return {"resources": list(resources.values())}
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des ressources", exc_info=True)
        raise HTTPException(500, "Failed to retrieve resources")