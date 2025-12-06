# app/routes/api/admin/recipes.py
"""
Routes Admin pour la gestion des recettes - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from utils.roles import require_admin
from utils.logger import get_logger
from utils.db_crud import recipe_crud, resource_crud, profession_crud
from database.connection import get_db
from models import Recipe
from schemas.recipe import RecipeCreate, RecipeUpdate, RecipeResponse

logger = get_logger(__name__)

router = APIRouter(
    prefix="/recipes", 
    tags=["Admin - Recipes"], 
    dependencies=[Depends(require_admin)]
)


# ============================================================================
# ROUTES CRUD
# ============================================================================

@router.get("/", response_model=List[RecipeResponse])
def list_recipes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    profession: str = Query(None, description="Filtrer par profession requise"),
    db: Session = Depends(get_db)
):
    """
    Liste toutes les recettes avec pagination.
    
    - **skip**: Pagination - nombre d'éléments à sauter
    - **limit**: Pagination - nombre max d'éléments
    - **profession**: Filtre optionnel par profession
    """
    logger.info(f"📋 Admin: Liste des recettes (skip={skip}, limit={limit}, profession={profession})")
    
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
    """Récupère une recette par son ID."""
    logger.info(f"🔍 Admin: Récupération recette '{recipe_id}'")
    
    recipe = recipe_crud.get_or_404(db, recipe_id, "Recipe")
    
    logger.debug(f"   → Recette '{recipe_id}' récupérée")
    return recipe


@router.post("/", response_model=RecipeResponse, status_code=201)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle recette.
    
    Valide automatiquement que :
    - La profession existe
    - La ressource de sortie existe
    - Tous les ingrédients existent
    """
    logger.info(f"➕ Admin: Création recette '{recipe.id}'")
    
    # Vérifie que l'ID n'existe pas déjà
    existing = recipe_crud.get(db, recipe.id)
    if existing:
        logger.warning(f"⚠️  Recette '{recipe.id}' existe déjà")
        raise HTTPException(400, f"Recipe '{recipe.id}' already exists")
    
    # VALIDATION MÉTIER
    
    # 1. Vérifie que la profession existe
    profession = profession_crud.get(db, recipe.required_profession)
    if not profession:
        logger.warning(f"⚠️  Profession '{recipe.required_profession}' inconnue")
        raise HTTPException(400, f"Profession '{recipe.required_profession}' not found")
    
    # 2. Vérifie que la ressource de sortie existe
    output_resource = resource_crud.get(db, recipe.output)
    if not output_resource:
        logger.warning(f"⚠️  Ressource de sortie '{recipe.output}' inconnue")
        raise HTTPException(400, f"Output resource '{recipe.output}' not found")
    
    # 3. Vérifie que tous les ingrédients existent
    for ingredient_id in recipe.ingredients.keys():
        ingredient = resource_crud.get(db, ingredient_id)
        if not ingredient:
            logger.warning(f"⚠️  Ingrédient '{ingredient_id}' inconnu")
            raise HTTPException(400, f"Ingredient '{ingredient_id}' not found")
    
    # Crée la recette
    new_recipe = recipe_crud.create(db, obj_in=recipe.model_dump())
    
    logger.info(f"✅ Recette '{recipe.id}' créée avec succès")
    return new_recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: str,
    recipe: RecipeUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une recette existante."""
    logger.info(f"✏️  Admin: Mise à jour recette '{recipe_id}'")
    
    # Filtre les champs None
    update_data = recipe.model_dump(exclude_unset=True)
    
    if not update_data:
        logger.warning(f"⚠️  Aucun champ à mettre à jour pour '{recipe_id}'")
        raise HTTPException(400, "No fields to update")
    
    logger.debug(f"   → Champs à mettre à jour: {list(update_data.keys())}")
    
    # VALIDATION si profession changée
    if "required_profession" in update_data:
        prof = profession_crud.get(db, update_data["required_profession"])
        if not prof:
            raise HTTPException(400, f"Profession '{update_data['required_profession']}' not found")
    
    # VALIDATION si output changé
    if "output" in update_data:
        res = resource_crud.get(db, update_data["output"])
        if not res:
            raise HTTPException(400, f"Output resource '{update_data['output']}' not found")
    
    # VALIDATION si ingrédients changés
    if "ingredients" in update_data:
        for ingredient_id in update_data["ingredients"].keys():
            res = resource_crud.get(db, ingredient_id)
            if not res:
                raise HTTPException(400, f"Ingredient '{ingredient_id}' not found")
    
    updated = recipe_crud.update_by_id(db, id=recipe_id, obj_in=update_data)
    
    logger.info(f"✅ Recette '{recipe_id}' mise à jour")
    return updated


@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: str,
    db: Session = Depends(get_db)
):
    """
    Supprime une recette.
    
    ⚠️ Attention: Cette action est irréversible.
    """
    logger.info(f"🗑️  Admin: Suppression recette '{recipe_id}'")
    
    recipe_crud.delete(db, id=recipe_id)
    
    logger.info(f"✅ Recette '{recipe_id}' supprimée")
    return {"status": "deleted", "id": recipe_id}


# ============================================================================
# ROUTES CUSTOM / STATS
# ============================================================================

@router.get("/stats/by-profession")
def recipes_stats_by_profession(db: Session = Depends(get_db)):
    """
    Statistiques: nombre de recettes par profession.
    
    Retourne un dictionnaire {profession: count}
    """
    logger.info("📊 Admin: Stats recettes par profession")
    
    from sqlalchemy import func
    
    result = (
        db.query(Recipe.required_profession, func.count(Recipe.id))
        .group_by(Recipe.required_profession)
        .all()
    )
    
    stats = {prof: count for prof, count in result}
    
    logger.debug(f"   → {len(stats)} profession(s)")
    return stats


@router.get("/validate/{recipe_id}")
def validate_recipe_integrity(
    recipe_id: str,
    db: Session = Depends(get_db)
):
    """
    Valide l'intégrité d'une recette.
    
    Vérifie que tous les ingrédients et l'output existent.
    """
    logger.info(f"✅ Admin: Validation recette '{recipe_id}'")
    
    recipe = recipe_crud.get_or_404(db, recipe_id, "Recipe")
    
    errors = []
    warnings = []
    
    # Vérifie la profession
    prof = profession_crud.get(db, recipe.required_profession)
    if not prof:
        errors.append(f"Profession '{recipe.required_profession}' not found")
    
    # Vérifie l'output
    output_res = resource_crud.get(db, recipe.output)
    if not output_res:
        errors.append(f"Output resource '{recipe.output}' not found")
    
    # Vérifie les ingrédients
    for ingredient_id in recipe.ingredients.keys():
        res = resource_crud.get(db, ingredient_id)
        if not res:
            errors.append(f"Ingredient '{ingredient_id}' not found")
    
    # Warnings
    if recipe.required_level > 50:
        warnings.append(f"High level requirement: {recipe.required_level}")
    
    if len(recipe.ingredients) > 5:
        warnings.append(f"Many ingredients: {len(recipe.ingredients)}")
    
    return {
        "recipe_id": recipe_id,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }