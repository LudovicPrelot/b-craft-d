# app/schemas/user.py
"""
Schémas Pydantic pour les utilisateurs.
"""

from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Dict, List, Optional


class UserBase(BaseModel):
    """Champs communs (sans password)."""
    firstname: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    mail: EmailStr
    login: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schéma pour la création (avec password)."""
    password: str = Field(..., min_length=6, max_length=100)
    profession: str = Field(default="", max_length=50)


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour."""
    firstname: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    mail: Optional[EmailStr] = None
    profession: Optional[str] = Field(None, max_length=50)
    subclasses: Optional[List[str]] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes = True)

    """Réponse publique (SANS password_hash)."""
    id: str
    profession: str
    subclasses: List[str]
    inventory: Dict[str, int]
    xp: int
    level: int
    stats: Dict[str, int]
    biome: str
    is_admin: bool
    is_moderator: bool


class UserProfileResponse(UserBase):
    model_config = ConfigDict(from_attributes = True)

    """Profil utilisateur (version simplifiée)."""
    id: str
    profession: str
    level: int