# app/routes/api/user/resources.py

from http.client import HTTPException
from fastapi import APIRouter, Depends
from utils.roles import require_player
from utils.logger import get_logger
from utils.json import load_json
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Users - Resources"], dependencies=[Depends(require_player)])

@router.get("/")
def list_resources(current=Depends(require_player)):
    logger.info(f"📦 Liste des ressources pour user_id={current.get('id')}")
    try:
        resources = list(load_json(config.RESOURCES_FILE).values())
        logger.debug(f"   → {len(resources)} ressource(s) disponible(s)")
        return resources
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des ressources", exc_info=True)
        raise HTTPException(500, "Failed to retrieve resources")
