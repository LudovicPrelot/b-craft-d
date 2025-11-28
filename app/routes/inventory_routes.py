# routes/inventory_routes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from utils.deps import require_user
from utils.storage import load_json, save_json
from services.inventory_service import add_item, remove_item, clear_inventory
from models.user import User
import config

router = APIRouter(prefix="/inventory", tags=["Inventory"])

def load_users():
    return load_json(config.USERS_FILE)

def save_users(data):
    save_json(config.USERS_FILE, data)


@router.get("/")
def get_inventory(current=Depends(require_user)):
    user = User.from_dict(current)
    return user.inventory


@router.post("/add")
def add_item_route(item: str = Query(...), qty: int = Query(1), current=Depends(require_user)):
    users = load_users()
    user = User.from_dict(current)

    add_item(user, item, qty)

    users[user.id] = user.to_dict()
    save_users(users)

    return {"status": "ok", "inventory": user.inventory}


@router.post("/remove")
def remove_item_route(item: str = Query(...), qty: int = Query(1), current=Depends(require_user)):
    users = load_users()
    user = User.from_dict(current)

    ok = remove_item(user, item, qty)
    if not ok:
        raise HTTPException(400, "Quantité insuffisante ou item manquant")

    users[user.id] = user.to_dict()
    save_users(users)

    return {"status": "ok", "inventory": user.inventory}


@router.post("/clear")
def clear_inventory_route(current=Depends(require_user)):
    users = load_users()
    user = User.from_dict(current)

    clear_inventory(user)

    users[user.id] = user.to_dict()
    save_users(users)

    return {"status": "cleared"}
