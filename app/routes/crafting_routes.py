# routes/crafting_routes.py

from fastapi import APIRouter, Depends, HTTPException
from utils.roles import require_player
from utils.json import load_json, save_json
import config
from models.user import User
from services.crafting_service import possible_recipes_for_user, apply_craft

router = APIRouter(prefix="/crafting", tags=["Crafting"])

def load_users():
    return load_json(config.USERS_FILE)

def save_users(data):
    save_json(config.USERS_FILE, data)

@router.get("/possible")
def list_possible(current=Depends(require_player)):
    user = User.from_dict(current)
    return possible_recipes_for_user(user)

@router.post("/craft")
def craft(payload: dict, current=Depends(require_player)):
    recipe_id = payload.get("recipe_id")
    if not recipe_id:
        raise HTTPException(400, "recipe_id manquant")

    users = load_users()
    user = User.from_dict(current)

    try:
        new_inv, produced = apply_craft(user, recipe_id)
    except Exception as e:
        raise HTTPException(400, str(e))

    users[user.id] = user.to_dict()
    save_users(users)

    return {"status": "crafted", "inventory": new_inv, "produced": produced}
