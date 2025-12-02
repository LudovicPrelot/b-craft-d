# app/database/models/__init__.py
"""
Import centralisé de tous les modèles SQLAlchemy.
Permet de ne charger que les modèles nécessaires.
"""

from .user import User
from .profession import Profession
from .resource import Resource
from .recipe import Recipe
from .refresh_token import RefreshToken
from .loot_table import LootTable
from .quest import Quest
from .setting import Setting

# Pour la compatibilité avec l'ancien code
__all__ = [
    "User",
    "Profession",
    "Resource",
    "Recipe",
    "RefreshToken",
    "LootTable",
    "Quest",
    "Setting",
]