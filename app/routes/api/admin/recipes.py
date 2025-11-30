# app/routes/api/admin/recipes.py

from fastapi import APIRouter, Depends, Body
from utils.roles import require_admin
from utils.logger import get_logger
from utils.crud import list_all, get_one, create_one, update_one, delete_one
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/recipes", tags=["Admin - Recipes"], dependencies=[Depends(require_admin)])

@router.get("/")
def list_recipes():
    return list_all(config.RECIPES_FILE, "recipes", logger)

@router.get("/{recipe_id}")
def get_recipe(recipe_id: str):
    return get_one(config.RECIPES_FILE, recipe_id, "recipe", logger)

@router.post("/")
def create_recipe(payload: dict = Body(...)):
    return create_one(config.RECIPES_FILE, payload, "recipe", logger)

@router.put("/{recipe_id}")
def update_recipe(recipe_id: str, payload: dict = Body(...)):
    return update_one(config.RECIPES_FILE, recipe_id, payload, "recipe", logger)

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: str):
    return delete_one(config.RECIPES_FILE, recipe_id, "recipe", logger)