# app/services/crafting_service.py
"""
Service de crafting - VERSION POSTGRESQL
"""

from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from models import User, Recipe
from services.inventory_service import has_items, remove_item, add_item
from services.xp_service import add_xp
from utils.logger import get_logger

logger = get_logger(__name__)


def can_craft(db: Session, user: User, recipe: Recipe) -> Tuple[bool, str]:
    """
    Vérifie si un utilisateur peut crafter une recette.
    
    Args:
        db: Session SQLAlchemy
        user: Utilisateur
        recipe: Recette à vérifier
    
    Returns:
        (bool, str): (peut_crafter, raison_si_non)
    
    Example:
        can, reason = can_craft(db, user, recipe)
        if not can:
            return {"error": reason}
    """
    # Vérification profession
    if recipe.required_profession and recipe.required_profession != user.profession:
        logger.debug(f"   → Profession incorrecte: requis={recipe.required_profession}, possédé={user.profession}")
        return False, f"Profession '{recipe.required_profession}' requise"
    
    # Vérification niveau
    if recipe.required_level > user.level:
        logger.debug(f"   → Niveau insuffisant: requis={recipe.required_level}, possédé={user.level}")
        return False, f"Niveau {recipe.required_level} requis (actuel: {user.level})"
    
    # Vérification ingrédients
    if not has_items(user, recipe.ingredients):
        logger.debug(f"   → Ingrédients manquants")
        return False, "Ingrédients insuffisants"
    
    return True, ""


def possible_recipes_for_user(db: Session, user: User) -> List[Dict[str, Any]]:
    """
    Retourne la liste des recettes que l'utilisateur peut crafter.
    
    Args:
        db: Session SQLAlchemy
        user: Utilisateur
    
    Returns:
        Liste de dicts avec infos des recettes craftables
    """
    logger.info(f"🔍 Recherche recettes possibles pour user={user.id}")
    
    # Récupère toutes les recettes de la profession
    recipes = (
        db.query(Recipe)
        .filter(Recipe.required_profession == user.profession)
        .filter(Recipe.required_level <= user.level)
        .all()
    )
    
    # Filtre celles qui ont les ingrédients
    possible = []
    for recipe in recipes:
        can, _ = can_craft(db, user, recipe)
        if can:
            possible.append({
                "id": recipe.id,
                "output": recipe.output,
                "ingredients": recipe.ingredients,
                "required_level": recipe.required_level,
                "xp_reward": recipe.xp_reward,
            })
    
    logger.debug(f"   → {len(possible)} recette(s) possible(s)")
    return possible


def apply_craft(
    db: Session, 
    user: User, 
    recipe_id: str
) -> Tuple[Dict[str, int], Dict[str, Any]]:
    """
    Exécute le crafting d'une recette.
    
    - Vérifie les conditions
    - Retire les ingrédients
    - Ajoute le produit
    - Donne l'XP
    
    Args:
        db: Session SQLAlchemy
        user: Utilisateur
        recipe_id: ID de la recette
    
    Returns:
        (inventaire_mis_à_jour, info_produit)
    
    Raises:
        ValueError: Si conditions non remplies ou recette inconnue
    """
    logger.info(f"🛠️  Craft de '{recipe_id}' par user={user.id}")
    
    # Récupère la recette
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        logger.warning(f"⚠️  Recette '{recipe_id}' inconnue")
        raise ValueError(f"Recette '{recipe_id}' inconnue")
    
    # Vérifie les conditions
    can, reason = can_craft(db, user, recipe)
    if not can:
        logger.warning(f"⚠️  Craft impossible: {reason}")
        raise ValueError(reason)
    
    logger.debug(f"   → Retrait des ingrédients...")
    
    # Retire les ingrédients
    for ingredient, qty in recipe.ingredients.items():
        success = remove_item(db, user, ingredient, qty)
        if not success:
            # Rollback si échec (ne devrait pas arriver après can_craft)
            db.rollback()
            raise ValueError(f"Erreur lors du retrait de {ingredient}")
    
    logger.debug(f"   → Ajout du produit: {recipe.output}")
    
    # Ajoute le produit (quantity = 1 par défaut)
    add_item(db, user, recipe.output, 1)
    
    # Donne l'XP
    if recipe.xp_reward > 0:
        logger.debug(f"   → Ajout XP: {recipe.xp_reward}")
        old_level = user.level
        add_xp(user, recipe.xp_reward)
        
        if user.level > old_level:
            logger.info(f"   🎉 Level up! {old_level} → {user.level}")
    
    # Commit final
    db.commit()
    db.refresh(user)
    
    logger.info(f"✅ Craft réussi: {recipe.output}")
    
    produced = {
        "item": recipe.output,
        "quantity": 1,
        "xp_gained": recipe.xp_reward,
    }
    
    return user.inventory, produced