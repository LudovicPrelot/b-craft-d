"""
Module: models.workshop_biome
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from typing import Dict, Any
from database import Base


class WorkshopBiome(Base):
    """
    Modèle pour la table workshops_biomes (table d'association)
    
    Représente les biomes où un atelier peut être construit.
    Chaque workshop peut être limité à certains biomes spécifiques.
    
    Attributes:
        id (int): Identifiant unique
        workshop_id (int): Référence au workshop
        biome_id (int): Référence au biome
    
    Relations:
        workshop: Workshop concerné
        biome: Biome où l'atelier peut être construit
    
    Exemples:
        - Forge: Montagne, Plaine, Côte
        - Scierie: Forêt, Plaine
        - Fonderie: Montagne uniquement
        - Moulin: Plaine, Rivière
    """
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "workshops_biomes"
    
    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    
    workshop_id = Column(
        Integer,
        ForeignKey("workshops.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    biome_id = Column(
        Integer,
        ForeignKey("biomes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Contraintes
    __table_args__ = (
        UniqueConstraint(
            'workshop_id',
            'biome_id',
            name='unique_workshop_biome'
        ),
    )
    
    # Relations
    workshop = relationship(
        "Workshop",
        back_populates="biomes",
        lazy="joined"
    )
    
    biome = relationship(
        "Biome",
        lazy="joined"
    )
    
    # ==================== PROPRIÉTÉS CALCULÉES ====================
    
    @property
    def biome_name(self) -> str:
        """
        Retourne le nom du biome
        
        Returns:
            str: Nom du biome ou "Unknown"
        """
        return self.biome.name if self.biome else "Unknown"
    
    @property
    def workshop_name(self) -> str:
        """
        Retourne le nom du workshop
        
        Returns:
            str: Nom du workshop ou "Unknown"
        """
        return self.workshop.name if self.workshop else "Unknown"
    
    @property
    def biome_description(self) -> str:
        """
        Retourne la description du biome
        
        Returns:
            str: Description du biome
        """
        return self.biome.description if self.biome else ""
    
    # ==================== MÉTHODES MÉTIER ====================
    
    def is_available_in_biome(self, biome_id: int) -> bool:
        """
        Vérifie si le workshop est disponible dans le biome donné
        
        Args:
            biome_id (int): ID du biome à vérifier
        
        Returns:
            bool: True si disponible, False sinon
        """
        return self.biome_id == biome_id
    
    def get_biome_bonus(self) -> float:
        """
        Récupère le bonus du biome (si applicable)
        
        Note: Cette méthode peut être étendue si des bonus
        spécifiques par biome sont ajoutés dans le futur
        
        Returns:
            float: Multiplicateur de bonus (1.0 = pas de bonus)
        """
        # Placeholder pour futurs bonus de biomes
        # Ex: Forge en Montagne = +10% vitesse craft
        return 1.0
    
    # ==================== SÉRIALISATION ====================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit en dictionnaire
        
        Args:
            include_relations (bool): Inclure les détails des relations
        
        Returns:
            dict: Représentation JSON
        """
        data = {
            "id": self.id,
            "workshop_id": self.workshop_id,
            "biome_id": self.biome_id
        }
        
        if include_relations:
            if self.biome:
                data["biome"] = {
                    "id": self.biome.id,
                    "name": self.biome.name,
                    "description": self.biome.description
                }
            
            if self.workshop:
                data["workshop"] = {
                    "id": self.workshop.id,
                    "name": self.workshop.name,
                    "durability": self.workshop.durability,
                    "max_durability": self.workshop.max_durability,
                    "is_broken": self.workshop.is_broken
                }
        
        return data
    
    def __repr__(self) -> str:
        """Représentation string"""
        return (
            f"<WorkshopBiome(id={self.id}, "
            f"workshop='{self.workshop_name}', "
            f"biome='{self.biome_name}')>"
        )