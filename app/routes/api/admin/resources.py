# app/routes/api/admin/resources.py

from fastapi import APIRouter, Depends, Body
from utils.roles import require_admin
from utils.logger import get_logger
from utils.crud import list_all, get_one, create_one, update_one, delete_one
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Admin - Resources"], dependencies=[Depends(require_admin)])

@router.get("/")
def list_recipes():
    return list_all(config.RESOURCES_FILE, "resources", logger)

@router.get("/{recipe_id}")
def get_recipe(recipe_id: str):
    return get_one(config.RESOURCES_FILE, recipe_id, "resource", logger)

@router.post("/")
def create_recipe(payload: dict = Body(...)):
    return create_one(config.RESOURCES_FILE, payload, "resource", logger)

@router.put("/{recipe_id}")
def update_recipe(recipe_id: str, payload: dict = Body(...)):
    return update_one(config.RESOURCES_FILE, recipe_id, payload, "resource", logger)

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: str):
    return delete_one(config.RESOURCES_FILE, recipe_id, "resource", logger)