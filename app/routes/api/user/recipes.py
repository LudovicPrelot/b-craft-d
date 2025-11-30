# app/routes/api/user/recipes.py

from http.client import HTTPException
from fastapi import APIRouter, Depends
from utils.roles import require_player
from utils.logger import get_logger
from utils.json import load_json
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/recipes", tags=["Users - Recipes"], dependencies=[Depends(require_player)])

@router.get("/")
def list_recipes(current=Depends(require_player)):
    logger.info(f"📜 Liste des recettes pour user_id={current.get('id')}")
    try:
        recipes = list(load_json(config.RECIPES_FILE).values())
        logger.debug(f"   → {len(recipes)} recette(s) disponible(s)")
        return recipes
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des recettes", exc_info=True)
        raise HTTPException(500, "Failed to retrieve recipes")
