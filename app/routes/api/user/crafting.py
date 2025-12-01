# app/routes/api/user/crafting.py

from fastapi import APIRouter, Depends, HTTPException
from utils.roles import require_user
from utils.json import load_users, save_users
from utils.logger import get_logger
from models.user import User
from services.crafting_service import possible_recipes_for_user, apply_craft

logger = get_logger(__name__)

router = APIRouter(prefix="/crafting", tags=["Users - Crafting"], dependencies=[Depends(require_user)])

@router.get("/possible")
def list_possible(current=Depends(require_user)):
    user = User.from_dict(current)
    logger.info(f"🔍 Récupération des recettes possibles pour user_id={user.id}")
    
    try:
        recipes = possible_recipes_for_user(user)
        logger.debug(f"   → {len(recipes)} recette(s) disponible(s)")
        return recipes
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des recettes possibles", exc_info=True)
        raise HTTPException(500, "Failed to retrieve possible recipes")

@router.post("/craft")
def craft(payload: dict, current=Depends(require_user)):
    recipe_id = payload.get("recipe_id")
    
    if not recipe_id:
        logger.warning("⚠️  Tentative de craft sans recipe_id")
        raise HTTPException(400, "recipe_id manquant")

    users = load_users()
    user = User.from_dict(current)
    
    logger.info(f"🛠️  Craft de '{recipe_id}' par user_id={user.id}")

    try:
        logger.debug(f"   → Vérification des ingrédients et profession")
        new_inv, produced = apply_craft(user, recipe_id)
        
        users[user.id] = user.to_dict()
        save_users(users)
        
        logger.info(f"✅ Craft réussi: {produced['item']} x{produced['quantity']}")
        logger.debug(f"   → Nouvel inventaire: {new_inv}")
        
        return {"status": "crafted", "inventory": new_inv, "produced": produced}
        
    except Exception as e:
        logger.warning(f"⚠️  Échec du craft '{recipe_id}': {str(e)}")
        raise HTTPException(400, str(e))