# app/routes/api/public/recipes.py
from fastapi import APIRouter, HTTPException
from utils.json import load_json
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.get("")
def list_recipes():
    logger.info("🌍 Accès public: Liste des recettes")
    try:
        recipes = load_json(config.RECIPES_FILE)
        logger.debug(f"   → {len(recipes)} recette(s) disponible(s)")
        return {"recipes": list(recipes.values())}
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des recettes", exc_info=True)
        raise HTTPException(500, "Failed to retrieve recipes")