# app/schemas/resource.py
"""
Schémas Pydantic pour les ressources.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ResourceBase(BaseModel):
    """Champs communs à toutes les opérations Resource."""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la ressource")
    type: str = Field(..., min_length=1, max_length=50, description="Type de ressource (mineral, material, food, etc.)")
    description: str = Field(default="", max_length=1000, description="Description de la ressource")
    weight: float = Field(default=1.0, ge=0.0, description="Poids unitaire en kg")
    stack_size: int = Field(default=999, ge=1, le=9999, description="Taille maximale d'un stack")


class ResourceCreate(ResourceBase):
    """Schéma pour la création d'une ressource."""
    id: str = Field(..., min_length=1, max_length=50, description="Identifiant unique")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "fer",
                "name": "Fer",
                "type": "metal",
                "description": "Un métal robuste utilisé en construction",
                "weight": 2.5,
                "stack_size": 999
            }
        }


class ResourceUpdate(BaseModel):
    """Schéma pour la mise à jour d'une ressource (tous les champs optionnels)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    weight: Optional[float] = Field(None, ge=0.0)
    stack_size: Optional[int] = Field(None, ge=1, le=9999)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Fer forgé",
                "weight": 3.0
            }
        }


class ResourceResponse(ResourceBase):
    """Schéma pour la réponse API (inclut l'ID)."""
    id: str
    
    class Config:
        from_attributes = True  # Permet la conversion depuis SQLAlchemy models
        json_schema_extra = {
            "example": {
                "id": "fer",
                "name": "Fer",
                "type": "metal",
                "description": "Un métal robuste utilisé en construction",
                "weight": 2.5,
                "stack_size": 999
            }
        }