# app/routes/api/user/inventory.py
"""
Routes user pour la gestion d'inventaire - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from utils.roles import require_user
from utils.logger import get_logger
from utils.db_crud import user_crud
from database.connection import get_db
from services.inventory_service import add_item, remove_item, clear_inventory

logger = get_logger(__name__)

router = APIRouter(
    prefix="/inventory", 
    tags=["Users - Inventory"], 
    dependencies=[Depends(require_user)]
)


@router.get("/")
def get_inventory(
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Récupère l'inventaire complet de l'utilisateur.
    
    Returns:
        Dict {item_id: quantity}
    """
    user_id = current.get("id")
    logger.info(f"🎒 Récupération inventaire pour user={user_id}")
    
    # Récupère l'utilisateur depuis la DB pour avoir les données à jour
    user = user_crud.get_or_404(db, user_id, "User")
    
    inventory = user.inventory or {}
    logger.debug(f"   → {len(inventory)} type(s) d'item(s)")
    
    return inventory


@router.post("/add")
def add_item_route(
    item: str = Query(..., description="ID de l'item à ajouter"),
    qty: int = Query(1, ge=1, le=999, description="Quantité à ajouter"),
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Ajoute des items à l'inventaire.
    
    - **item**: ID de la ressource
    - **qty**: Quantité à ajouter (1-999)
    """
    user_id = current.get("id")
    logger.info(f"➕ Ajout {item} x{qty} pour user={user_id}")
    
    try:
        # Récupère l'utilisateur
        user = user_crud.get_or_404(db, user_id, "User")
        
        # Ajoute l'item
        inventory = add_item(db, user, item, qty)
        
        logger.info(f"✅ Item ajouté (total: {inventory.get(item, 0)})")
        
        return {
            "status": "ok",
            "inventory": inventory,
            "added": {
                "item": item,
                "quantity": qty
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur ajout item: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to add item: {str(e)}")


@router.post("/remove")
def remove_item_route(
    item: str = Query(..., description="ID de l'item à retirer"),
    qty: int = Query(1, ge=1, le=999, description="Quantité à retirer"),
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Retire des items de l'inventaire.
    
    - **item**: ID de la ressource
    - **qty**: Quantité à retirer (1-999)
    
    Retourne une erreur si quantité insuffisante.
    """
    user_id = current.get("id")
    logger.info(f"➖ Retrait {item} x{qty} pour user={user_id}")
    
    try:
        # Récupère l'utilisateur
        user = user_crud.get_or_404(db, user_id, "User")
        
        # Retire l'item
        success = remove_item(db, user, item, qty)
        
        if not success:
            logger.warning(f"⚠️  Quantité insuffisante ou item manquant")
            raise HTTPException(400, "Quantité insuffisante ou item manquant")
        
        logger.info(f"✅ Item retiré (reste: {user.inventory.get(item, 0)})")
        
        return {
            "status": "ok",
            "inventory": user.inventory,
            "removed": {
                "item": item,
                "quantity": qty
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur retrait item: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to remove item: {str(e)}")


@router.post("/clear")
def clear_inventory_route(
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Vide complètement l'inventaire de l'utilisateur.
    
    ⚠️ Action irréversible!
    """
    user_id = current.get("id")
    logger.info(f"🗑️  Vidage inventaire pour user={user_id}")
    
    try:
        # Récupère l'utilisateur
        user = user_crud.get_or_404(db, user_id, "User")
        
        # Vide l'inventaire
        clear_inventory(db, user)
        
        logger.info(f"✅ Inventaire vidé")
        
        return {
            "status": "cleared",
            "inventory": {}
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur vidage inventaire: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to clear inventory: {str(e)}")