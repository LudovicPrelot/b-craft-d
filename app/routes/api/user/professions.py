# app/routes/api/user/professions.py

from http.client import HTTPException
from fastapi import APIRouter, Depends
from utils.roles import require_player
from utils.logger import get_logger
from utils.json import load_json
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Users - Professions"], dependencies=[Depends(require_player)])

@router.get("/")
def list_professions(current=Depends(require_player)):
    logger.info(f"👷 Liste des professions pour user_id={current.get('id')}")
    try:
        professions = list(load_json(config.PROFESSIONS_FILE).values())
        logger.debug(f"   → {len(professions)} profession(s) disponible(s)")
        return professions
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des professions", exc_info=True)
        raise HTTPException(500, "Failed to retrieve professions")
