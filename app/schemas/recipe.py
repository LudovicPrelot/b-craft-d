# app/schemas/recipe.py
"""
Schémas Pydantic pour les recettes de crafting.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional


class RecipeBase(BaseModel):
    """Champs communs à toutes les opérations Recipe."""
    output: str = Field(..., min_length=1, max_length=50, description="ID de la ressource produite")
    ingredients: Dict[str, int] = Field(..., description="Ingrédients requis {resource_id: quantity}")
    required_profession: str = Field(..., min_length=1, max_length=50, description="Profession requise")
    required_level: int = Field(default=1, ge=1, le=100, description="Niveau requis")
    xp_reward: int = Field(default=10, ge=0, description="XP gagnée lors du craft")
    
    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        """Vérifie que les quantités sont positives."""
        if not v:
            raise ValueError("Recipe must have at least one ingredient")
        
        for resource_id, qty in v.items():
            if qty <= 0:
                raise ValueError(f"Ingredient quantity must be positive (got {qty} for {resource_id})")
        
        return v


class RecipeCreate(RecipeBase):
    """Schéma pour la création d'une recette."""
    id: str = Field(..., min_length=1, max_length=50, description="Identifiant unique")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ciment",
                "output": "ciment",
                "ingredients": {
                    "argile": 1,
                    "calcaire": 1
                },
                "required_profession": "mineur",
                "required_level": 1,
                "xp_reward": 10
            }
        }


class RecipeUpdate(BaseModel):
    """Schéma pour la mise à jour d'une recette."""
    output: Optional[str] = Field(None, min_length=1, max_length=50)
    ingredients: Optional[Dict[str, int]] = None
    required_profession: Optional[str] = Field(None, min_length=1, max_length=50)
    required_level: Optional[int] = Field(None, ge=1, le=100)
    xp_reward: Optional[int] = Field(None, ge=0)
    
    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        """Vérifie que les quantités sont positives."""
        if v is not None:
            if not v:
                raise ValueError("Recipe must have at least one ingredient")
            
            for resource_id, qty in v.items():
                if qty <= 0:
                    raise ValueError(f"Ingredient quantity must be positive (got {qty} for {resource_id})")
        
        return v


class RecipeResponse(RecipeBase):
    """Schéma pour la réponse API."""
    id: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "ciment",
                "output": "ciment",
                "ingredients": {
                    "argile": 1,
                    "calcaire": 1
                },
                "required_profession": "mineur",
                "required_level": 1,
                "xp_reward": 10
            }
        }