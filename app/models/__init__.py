# app/models/__init__.py
"""
Import centralisé de tous les modèles SQLAlchemy.
Permet de ne charger que les modèles nécessaires.
"""

from .user import User
from .profession import Profession
from .resource import Resource
from .recipe import Recipe
from .refresh_token import RefreshToken

# Pour la compatibilité avec l'ancien code
__all__ = [
    "User",
    "Profession",
    "Resource",
    "Recipe",
    "RefreshToken",
]