# services/crafting_service.py

from typing import Dict, Any, Tuple, List
import json
import config
from utils.storage import load_json, save_json
from models.user import User

def _load_recipes() -> Dict[str, dict]:
    try:
        return load_json(config.RECIPES_FILE)
    except Exception:
        return {}

def can_craft(user: User, recipe: dict) -> bool:
    # check profession
    req_prof = recipe.get("required_profession")
    if req_prof and req_prof != user.profession:
        return False
    # check ingredients
    ingredients = recipe.get("ingredients", {})
    for res, qty in ingredients.items():
        if user.inventory.get(res, 0) < qty:
            return False
    return True

def possible_recipes_for_user(user: User) -> List[dict]:
    recipes = _load_recipes()
    out = []
    for rid, r in recipes.items():
        if can_craft(user, r):
            out.append({"id": rid, "output": r.get("output"), "ingredients": r.get("ingredients")})
    return out

def apply_craft(user: User, recipe_id: str) -> Tuple[Dict[str,int], Dict[str,Any]]:
    recipes = _load_recipes()
    if recipe_id not in recipes:
        raise ValueError("Recette inconnue")
    recipe = recipes[recipe_id]
    if not can_craft(user, recipe):
        raise ValueError("Conditions non satisfaites (profession/ingrédients)")

    # debit ingredients
    for res, qty in recipe.get("ingredients", {}).items():
        current = user.inventory.get(res, 0)
        if current < qty:
            raise ValueError(f"Ressource insuffisante: {res}")
        user.inventory[res] = current - qty
        if user.inventory[res] <= 0:
            del user.inventory[res]

    # add output
    out_id = recipe.get("output")
    user.inventory[out_id] = user.inventory.get(out_id, 0) + 1

    produced = {"id": recipe_id, "output": out_id}
    return user.inventory, produced
