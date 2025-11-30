# app/routes/api/public/recipes.py

from fastapi import APIRouter
from utils.logger import get_logger
from utils.crud import list_all
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/recipes", tags=["Public - Recipes"])

@router.get("/")
def list_recipes():
    items = list_all(config.RECIPES_FILE, "recipes", logger)
    return {"recipes": items}  # Format public avec clé