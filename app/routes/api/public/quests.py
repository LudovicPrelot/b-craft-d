# app/routes/api/public/quests.py
from fastapi import APIRouter, Depends, HTTPException
from utils.json import load_json
from utils.logger import get_logger
from utils.feature_flags import require_feature
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/quests", tags=["Quests"], dependencies=[Depends(require_feature("enable_quests"))])

@router.get("/")
def list_quests():
    logger.info("📜 Liste des quêtes disponibles")
    try:
        quests = load_json(config.QUESTS_FILE)
        logger.debug(f"   → {len(quests)} quête(s) disponible(s)")
        return quests
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des quêtes", exc_info=True)
        raise HTTPException(500, "Failed to retrieve quests")