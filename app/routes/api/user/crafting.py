# app/routes/api/user/crafting.py
"""
Routes user pour le crafting - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from utils.roles import require_user
from utils.logger import get_logger
from utils.db_crud import user_crud
from database.connection import get_db
from services.crafting_service import possible_recipes_for_user, apply_craft

logger = get_logger(__name__)

router = APIRouter(
    prefix="/crafting", 
    tags=["Users - Crafting"], 
    dependencies=[Depends(require_user)]
)


@router.get("/possible")
def list_possible_recipes(
    current=Depends(require_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Liste toutes les recettes que l'utilisateur peut crafter actuellement.
    
    Vérifie:
    - Profession correspondante
    - Niveau suffisant
    - Ingrédients disponibles dans l'inventaire
    
    Returns:
        Liste de recettes craftables
    """
    user_id = current.get("id")
    logger.info(f"🔍 Recettes possibles pour user={user_id}")
    
    try:
        # Récupère l'utilisateur
        user = user_crud.get_or_404(db, user_id, "User")
        
        # Récupère les recettes possibles
        recipes = possible_recipes_for_user(db, user)
        
        logger.debug(f"   → {len(recipes)} recette(s) disponible(s)")
        
        return recipes
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération recettes: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to retrieve recipes: {str(e)}")


@router.post("/craft")
def craft_recipe(
    payload: Dict[str, str] = Body(...),
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Exécute le crafting d'une recette.
    
    **Payload:**
    - recipe_id: ID de la recette à crafter
    
    **Process:**
    1. Vérifie profession, niveau, ingrédients
    2. Retire les ingrédients de l'inventaire
    3. Ajoute le produit crafté
    4. Donne l'XP
    5. Vérifie level up
    
    **Returns:**
    - status: "crafted"
    - inventory: Inventaire mis à jour
    - produced: Infos sur le produit créé
    - level_up: True si level up, False sinon
    """
    recipe_id = payload.get("recipe_id")
    
    if not recipe_id:
        logger.warning("⚠️  Tentative craft sans recipe_id")
        raise HTTPException(400, "recipe_id manquant")
    
    user_id = current.get("id")
    logger.info(f"🛠️  Craft '{recipe_id}' par user={user_id}")
    
    try:
        # Récupère l'utilisateur
        user = user_crud.get_or_404(db, user_id, "User")
        
        # Sauvegarde niveau avant craft
        old_level = user.level
        
        # Exécute le craft
        new_inv, produced = apply_craft(db, user, recipe_id)
        
        # Vérifie level up
        level_up = user.level > old_level
        
        if level_up:
            logger.info(f"   🎉 Level up! {old_level} → {user.level}")
        
        logger.info(f"✅ Craft réussi: {produced['item']} x{produced['quantity']}")
        
        return {
            "status": "crafted",
            "inventory": new_inv,
            "produced": produced,
            "level_up": level_up,
            "new_level": user.level if level_up else None,
        }
        
    except ValueError as e:
        # Erreur de validation (conditions non remplies)
        logger.warning(f"⚠️  Craft impossible: {str(e)}")
        raise HTTPException(400, str(e))
        
    except Exception as e:
        logger.error(f"❌ Erreur durant le craft: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to craft: {str(e)}")