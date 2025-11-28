# services/inventory_service.py

from models.user import User

def add_item(user: User, item: str, qty: int = 1):
    if qty <= 0:
        return
    user.inventory[item] = user.inventory.get(item, 0) + qty

def remove_item(user: User, item: str, qty: int = 1):
    if item not in user.inventory:
        return False
    if user.inventory[item] < qty:
        return False
    user.inventory[item] -= qty
    if user.inventory[item] <= 0:
        del user.inventory[item]
    return True

def clear_inventory(user: User):
    user.inventory = {}
