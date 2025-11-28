# routes/public_routes.py

from fastapi import APIRouter
from utils.storage import load_json
import config

router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/resources")
def list_ingredients():
    resources = load_json(config.RESOURCES_FILE)
    return {"resources": list(resources.values())}

@router.get("/recipes")
def list_recipes():
    recipes = load_json(config.RECIPES_FILE)
    return {"recipes": list(recipes.values())}

@router.get("/professions")
def list_professions():
    professions = load_json(config.PROFESSIONS_FILE)
    return {"professions": list(professions.values())}
