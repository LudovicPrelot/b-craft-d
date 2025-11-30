# app/routes/api/user/devices.py

from fastapi import APIRouter, Depends, HTTPException, Query
from utils.roles import require_player
from utils.json import load_users, save_users
from utils.logger import get_logger
from services.inventory_service import add_item, remove_item, clear_inventory
from models.user import User

logger = get_logger(__name__)

router = APIRouter(prefix="/inventory", tags=["Users - Inventory"], dependencies=[Depends(require_player)])

@router.get("/")
def get_inventory(current=Depends(require_player)):
    user = User.from_dict(current)
    logger.info(f"🎒 Récupération de l'inventaire pour user_id={user.id}")
    logger.debug(f"   → {len(user.inventory)} type(s) d'item(s)")
    return user.inventory


@router.post("/add")
def add_item_route(item: str = Query(...), qty: int = Query(1), current=Depends(require_player)):
    users = load_users()
    user = User.from_dict(current)
    
    logger.info(f"➕ Ajout de {item} x{qty} à l'inventaire de user_id={user.id}")

    try:
        add_item(user, item, qty)
        users[user.id] = user.to_dict()
        save_users(users)
        
        logger.info(f"✅ Item ajouté avec succès (total: {user.inventory.get(item, 0)})")
        return {"status": "ok", "inventory": user.inventory}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout de l'item", exc_info=True)
        raise HTTPException(500, "Failed to add item")


@router.post("/remove")
def remove_item_route(item: str = Query(...), qty: int = Query(1), current=Depends(require_player)):
    users = load_users()
    user = User.from_dict(current)
    
    logger.info(f"➖ Retrait de {item} x{qty} de l'inventaire de user_id={user.id}")

    try:
        ok = remove_item(user, item, qty)
        if not ok:
            logger.warning(f"⚠️  Quantité insuffisante ou item manquant")
            raise HTTPException(400, "Quantité insuffisante ou item manquant")

        users[user.id] = user.to_dict()
        save_users(users)
        
        logger.info(f"✅ Item retiré avec succès (reste: {user.inventory.get(item, 0)})")
        return {"status": "ok", "inventory": user.inventory}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors du retrait de l'item", exc_info=True)
        raise HTTPException(500, "Failed to remove item")


@router.post("/clear")
def clear_inventory_route(current=Depends(require_player)):
    users = load_users()
    user = User.from_dict(current)
    
    logger.info(f"🗑️  Vidage de l'inventaire de user_id={user.id}")

    try:
        clear_inventory(user)
        users[user.id] = user.to_dict()
        save_users(users)
        
        logger.info(f"✅ Inventaire vidé avec succès")
        return {"status": "cleared"}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du vidage de l'inventaire", exc_info=True)
        raise HTTPException(500, "Failed to clear inventory")