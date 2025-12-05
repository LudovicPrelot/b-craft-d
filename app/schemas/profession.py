# app/schemas/profession.py
"""
Schémas Pydantic pour les professions.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class ProfessionBase(BaseModel):
    """Champs communs à toutes les opérations Profession."""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la profession")
    description: str = Field(default="", max_length=2000, description="Description détaillée")
    resources_found: List[str] = Field(default_factory=list, description="IDs des ressources trouvables")
    allowed_recipes: List[str] = Field(default_factory=list, description="IDs des recettes autorisées")
    subclasses: List[str] = Field(default_factory=list, description="Sous-classes/spécialisations")


class ProfessionCreate(ProfessionBase):
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "id": "mineur",
                "name": "Mineur",
                "description": "Expert en extraction de minerais",
                "resources_found": ["argile", "calcaire", "fer", "or"],
                "allowed_recipes": ["ciment"],
                "subclasses": ["foreur", "géologue", "prospecteur"]
            }
        }
    )

    """Schéma pour la création d'une profession."""
    id: str = Field(..., min_length=1, max_length=50, description="Identifiant unique")


class ProfessionUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "description": "Expert en extraction et transformation de minerais",
                "subclasses": ["foreur", "géologue", "prospecteur", "sismologue"]
            }
        }
    )
    
    """Schéma pour la mise à jour d'une profession."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    resources_found: Optional[List[str]] = None
    allowed_recipes: Optional[List[str]] = None
    subclasses: Optional[List[str]] = None


class ProfessionResponse(ProfessionBase):
    model_config = ConfigDict(
        from_attributes = True,
        json_schema_extra = {
            "example": {
                "id": "mineur",
                "name": "Mineur",
                "description": "Expert en extraction de minerais",
                "resources_found": ["argile", "calcaire", "fer", "or"],
                "allowed_recipes": ["ciment"],
                "subclasses": ["foreur", "géologue", "prospecteur"]
            }
        }
    )
    
    """Schéma pour la réponse API."""
    id: str