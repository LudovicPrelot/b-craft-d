# app/services/inventory_service.py
"""
Service de gestion d'inventaire - VERSION POSTGRESQL
"""

from sqlalchemy.orm import Session
from models import User
from utils.logger import get_logger

logger = get_logger(__name__)


def add_item(db: Session, user: User, item: str, qty: int = 1) -> dict:
    """
    Ajoute des items à l'inventaire d'un utilisateur.
    
    Args:
        db: Session SQLAlchemy
        user: Utilisateur
        item: ID de l'item
        qty: Quantité à ajouter
    
    Returns:
        Inventaire mis à jour
    """
    if qty <= 0:
        logger.warning(f"⚠️  Tentative d'ajout quantité invalide: {qty}")
        return user.inventory
    
    logger.debug(f"➕ Ajout {item} x{qty} pour user={user.id}")
    
    # Mise à jour de l'inventaire
    if user.inventory is None:
        user.inventory = {}
    
    user.inventory[item] = user.inventory.get(item, 0) + qty
    
    # Commit en base
    db.commit()
    db.refresh(user)
    
    logger.debug(f"   → Total {item}: {user.inventory[item]}")
    
    return user.inventory


def remove_item(db: Session, user: User, item: str, qty: int = 1) -> bool:
    """
    Retire des items de l'inventaire d'un utilisateur.
    
    Args:
        db: Session SQLAlchemy
        user: Utilisateur
        item: ID de l'item
        qty: Quantité à retirer
    
    Returns:
        True si succès, False si quantité insuffisante
    """
    if qty <= 0:
        logger.warning(f"⚠️  Tentative de retrait quantité invalide: {qty}")
        return False
    
    logger.debug(f"➖ Retrait {item} x{qty} pour user={user.id}")
    
    # Vérifications
    if user.inventory is None or item not in user.inventory:
        logger.warning(f"⚠️  Item {item} non trouvé dans l'inventaire")
        return False
    
    if user.inventory[item] < qty:
        logger.warning(f"⚠️  Quantité insuffisante: {user.inventory[item]} < {qty}")
        return False
    
    # Mise à jour
    user.inventory[item] -= qty
    
    # Supprime la clé si quantité = 0
    if user.inventory[item] <= 0:
        del user.inventory[item]
        logger.debug(f"   → {item} retiré complètement de l'inventaire")
    else:
        logger.debug(f"   → Reste {item}: {user.inventory[item]}")
    
    # Commit en base
    db.commit()
    db.refresh(user)
    
    return True


def clear_inventory(db: Session, user: User) -> None:
    """
    Vide complètement l'inventaire d'un utilisateur.
    
    Args:
        db: Session SQLAlchemy
        user: Utilisateur
    """
    logger.info(f"🗑️  Vidage inventaire pour user={user.id}")
    
    user.inventory = {}
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"✅ Inventaire vidé")


def get_inventory_weight(user: User) -> float:
    """
    Calcule le poids total de l'inventaire.
    
    Note: Nécessite d'avoir les ressources chargées pour connaître leur poids.
    
    Args:
        user: Utilisateur
    
    Returns:
        Poids total en kg
    """
    # TODO: Implémenter calcul basé sur Resource.weight
    # Pour l'instant, retourne 0
    return 0.0


def has_items(user: User, requirements: dict) -> bool:
    """
    Vérifie si l'utilisateur possède les items requis.
    
    Args:
        user: Utilisateur
        requirements: Dict {item_id: quantity}
    
    Returns:
        True si tous les items sont présents en quantité suffisante
    
    Example:
        if has_items(user, {"argile": 2, "calcaire": 1}):
            # Peut crafter
    """
    if user.inventory is None:
        return False
    
    for item, qty in requirements.items():
        if user.inventory.get(item, 0) < qty:
            logger.debug(f"   → Item manquant: {item} (requis: {qty}, possédé: {user.inventory.get(item, 0)})")
            return False
    
    return True