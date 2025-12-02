# app/routes/api/user/recipes.py
"""
Routes user pour les recettes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from utils.roles import require_user
from utils.logger import get_logger
from utils.db_crud import recipe_crud
from database.connection import get_db
from schemas.recipe import RecipeResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/recipes", tags=["Users - Recipes"], dependencies=[Depends(require_user)])


@router.get("/", response_model=List[RecipeResponse])
def list_recipes(
    profession: str = Query(None),
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Liste toutes les recettes.
    
    Peut filtrer par profession.
    """
    user_id = current.get("id")
    logger.info(f"📋 User {user_id}: Liste des recettes (profession={profession})")
    
    filters = {}
    if profession:
        filters["required_profession"] = profession
    
    recipes = recipe_crud.get_multi(db, limit=500, filters=filters)
    
    logger.debug(f"   → {len(recipes)} recette(s)")
    return recipes


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: str,
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """Récupère une recette."""
    user_id = current.get("id")
    logger.info(f"🔍 User {user_id}: Récupération recette '{recipe_id}'")
    
    recipe = recipe_crud.get_or_404(db, recipe_id, "Recipe")
    
    return recipe