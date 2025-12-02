# app/routes/api/public/recipes.py
"""
Routes publiques pour les recettes (lecture seule).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from utils.logger import get_logger
from utils.db_crud import recipe_crud
from database.connection import get_db
from schemas.recipe import RecipeResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/recipes", tags=["Public - Recipes"])


@router.get("/", response_model=List[RecipeResponse])
def list_recipes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    profession: str = Query(None, description="Filtrer par profession"),
    db: Session = Depends(get_db)
):
    """
    Liste toutes les recettes disponibles.
    
    Accessible sans authentification.
    """
    logger.info(f"📋 Public: Liste des recettes (skip={skip}, limit={limit}, profession={profession})")
    
    filters = {}
    if profession:
        filters["required_profession"] = profession
    
    recipes = recipe_crud.get_multi(db, skip=skip, limit=limit, filters=filters)
    
    logger.debug(f"   → {len(recipes)} recette(s) trouvée(s)")
    return recipes


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'une recette.
    
    Accessible sans authentification.
    """
    logger.info(f"🔍 Public: Récupération recette '{recipe_id}'")
    
    recipe = recipe_crud.get_or_404(db, recipe_id, "Recipe")
    
    logger.debug(f"   → Recette '{recipe_id}' récupérée")
    return recipe