# app/routes/public_routes.py

from fastapi import APIRouter, HTTPException
from utils.json import load_json
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/resources")
def list_ingredients():
    logger.info("🌍 Accès public: Liste des ressources")
    try:
        resources = load_json(config.RESOURCES_FILE)
        logger.debug(f"   → {len(resources)} ressource(s) disponible(s)")
        return {"resources": list(resources.values())}
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des ressources", exc_info=True)
        raise HTTPException(500, "Failed to retrieve resources")

@router.get("/recipes")
def list_recipes():
    logger.info("🌍 Accès public: Liste des recettes")
    try:
        recipes = load_json(config.RECIPES_FILE)
        logger.debug(f"   → {len(recipes)} recette(s) disponible(s)")
        return {"recipes": list(recipes.values())}
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des recettes", exc_info=True)
        raise HTTPException(500, "Failed to retrieve recipes")

@router.get("/professions")
def list_professions():
    logger.info("🌍 Accès public: Liste des professions")
    try:
        professions = load_json(config.PROFESSIONS_FILE)
        logger.debug(f"   → {len(professions)} profession(s) disponible(s)")
        return {"professions": list(professions.values())}
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des professions", exc_info=True)
        raise HTTPException(500, "Failed to retrieve professions")