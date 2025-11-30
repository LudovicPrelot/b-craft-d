# app/routes/api/user/recipes.py

from fastapi import APIRouter, Depends
from utils.roles import require_player
from utils.logger import get_logger
from utils.crud import list_all, get_one
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/recipes", tags=["User - Recipes"], dependencies=[Depends(require_player)])

@router.get("/")
def list_recipes(current=Depends(require_player)):
    user_id = current.get("id")
    return list_all(config.RECIPES_FILE, "recipes", logger, user_id=user_id)

@router.get("/{recipe_id}")
def get_recipe(recipe_id: str, current=Depends(require_player)):
    user_id = current.get("id")
    return get_one(config.RECIPES_FILE, recipe_id, "recipe", logger, user_id=user_id)