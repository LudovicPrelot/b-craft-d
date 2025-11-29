# app/routes/recipes_routes.py

from fastapi import APIRouter, Depends, HTTPException
from utils.json import load_json, save_json
from utils.roles import require_player
from utils.roles import require_moderator
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/recipes", tags=["Recipes"])


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


@router.post("/", dependencies=[Depends(require_moderator)])
def create_recipe(payload):
    recipe_id = payload.get("id")
    logger.info(f"➕ Modérateur: Création de la recette '{recipe_id}'")
    
    try:
        data = load_json(config.RECIPES_FILE)
        if payload["id"] in data:
            logger.warning(f"⚠️  Recette '{recipe_id}' existe déjà")
            raise HTTPException(400, "Recipe already exists")
        
        data[payload["id"]] = payload
        save_json(config.RECIPES_FILE, data)
        
        logger.info(f"✅ Recette '{recipe_id}' créée avec succès")
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la recette", exc_info=True)
        raise HTTPException(500, "Failed to create recipe")


@router.delete("/{rid}", dependencies=[Depends(require_moderator)])
def delete_recipe(rid: str):
    logger.info(f"🗑️  Modérateur: Suppression de la recette '{rid}'")
    
    try:
        data = load_json(config.RECIPES_FILE)
        if rid not in data:
            logger.warning(f"⚠️  Recette '{rid}' non trouvée")
            raise HTTPException(404, "Recipe not found")
        
        del data[rid]
        save_json(config.RECIPES_FILE, data)
        
        logger.info(f"✅ Recette '{rid}' supprimée avec succès")
        return {"status": "deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de la recette", exc_info=True)
        raise HTTPException(500, "Failed to delete recipe")