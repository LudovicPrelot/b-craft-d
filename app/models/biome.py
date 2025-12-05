# app/models/biome.py

from sqlalchemy import Column, Integer, String, Text, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from datetime import datetime
from typing import Dict, Any, List

from database import Base


class Biome(Base):
    """
    Modèle pour la table biomes
    
    Représente les zones géographiques du monde du jeu
    qui affectent les multiplicateurs de gathering et
    la disponibilité des ressources.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    __tablename__ = "biomes"
    
    # =========================================================================
    # COLONNES
    # =========================================================================
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    gathering_multiplier = Column(
        Numeric(5, 2), 
        nullable=False, 
        default=1.00,
        doc="Multiplicateur de gathering spécifique à ce biome"
    )
    created_at = Column(
        "created_at",
        nullable=False,
        default=datetime.utcnow
    )
    
    # =========================================================================
    # CONTRAINTES
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            'gathering_multiplier >= 0',
            name='chk_biomes_gathering_multiplier'
        ),
    )
    
    # =========================================================================
    # RELATIONS
    # =========================================================================
    
    # Relation many-to-many avec resources via resources_biomes
    resources = relationship(
        "Resource",
        secondary="resources_biomes",
        back_populates="biomes",
        doc="Ressources disponibles dans ce biome"
    )
    
    # Relation many-to-many avec workshops via workshops_biomes
    workshops = relationship(
        "Workshop",
        secondary="workshops_biomes",
        back_populates="biomes",
        doc="Ateliers pouvant être construits dans ce biome"
    )
    
    # =========================================================================
    # PROPRIÉTÉS CALCULÉES
    # =========================================================================
    
    @property
    def is_favorable_for_gathering(self) -> bool:
        """
        Vérifie si le biome est favorable pour le gathering
        
        Returns:
            bool: True si multiplicateur > 1.0
        """
        return float(self.gathering_multiplier) > 1.0
    
    @property
    def gathering_bonus_percent(self) -> float:
        """
        Calcule le bonus/malus de gathering en pourcentage
        
        Returns:
            float: Pourcentage (ex: 20.0 pour +20%, -10.0 pour -10%)
        """
        return (float(self.gathering_multiplier) - 1.0) * 100
    
    @property
    def resources_count(self) -> int:
        """
        Compte le nombre de ressources disponibles dans ce biome
        
        Returns:
            int: Nombre de ressources
        """
        return len(self.resources) if self.resources else 0
    
    @property
    def workshops_count(self) -> int:
        """
        Compte le nombre d'ateliers constructibles dans ce biome
        
        Returns:
            int: Nombre d'ateliers
        """
        return len(self.workshops) if self.workshops else 0
    
    # =========================================================================
    # MÉTHODES MÉTIER
    # =========================================================================
    
    def apply_gathering_multiplier(self, base_amount: float) -> float:
        """
        Applique le multiplicateur de gathering à une quantité de base
        
        Args:
            base_amount: Quantité de base récoltée
            
        Returns:
            float: Quantité ajustée après application du multiplicateur
        """
        return base_amount * float(self.gathering_multiplier)
    
    def has_resource(self, resource_id: int) -> bool:
        """
        Vérifie si une ressource est disponible dans ce biome
        
        Args:
            resource_id: ID de la ressource à vérifier
            
        Returns:
            bool: True si la ressource est disponible
        """
        if not self.resources:
            return False
        return any(r.id == resource_id for r in self.resources)
    
    def has_workshop(self, workshop_id: int) -> bool:
        """
        Vérifie si un atelier peut être construit dans ce biome
        
        Args:
            workshop_id: ID de l'atelier à vérifier
            
        Returns:
            bool: True si l'atelier peut être construit
        """
        if not self.workshops:
            return False
        return any(w.id == workshop_id for w in self.workshops)
    
    def get_resources_by_rarity(self, rarity_name: str) -> List:
        """
        Filtre les ressources de ce biome par rareté
        
        Args:
            rarity_name: Nom de la rareté (ex: "Rare", "Épique")
            
        Returns:
            List: Liste des ressources filtrées
        """
        if not self.resources:
            return []
        
        return [
            r for r in self.resources 
            if hasattr(r, 'rarity') and r.rarity.name == rarity_name
        ]
    
    def get_available_workshops_names(self) -> List[str]:
        """
        Récupère la liste des noms d'ateliers disponibles
        
        Returns:
            List[str]: Liste des noms d'ateliers
        """
        if not self.workshops:
            return []
        return [w.name for w in self.workshops]
    
    # =========================================================================
    # SÉRIALISATION
    # =========================================================================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit le modèle en dictionnaire
        
        Args:
            include_relations: Inclure les relations (ressources, ateliers)
            
        Returns:
            Dict: Représentation dictionnaire du modèle
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "gathering_multiplier": float(self.gathering_multiplier),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Propriétés calculées
            "is_favorable_for_gathering": self.is_favorable_for_gathering,
            "gathering_bonus_percent": self.gathering_bonus_percent,
            "resources_count": self.resources_count,
            "workshops_count": self.workshops_count
        }
        
        if include_relations:
            if self.resources:
                data["resources"] = [
                    {
                        "id": r.id,
                        "name": r.name,
                        "rarity": r.rarity.name if hasattr(r, 'rarity') else None
                    } 
                    for r in self.resources
                ]
            
            if self.workshops:
                data["workshops"] = [
                    {"id": w.id, "name": w.name} 
                    for w in self.workshops
                ]
        
        return data
    
    # =========================================================================
    # MÉTHODES MAGIQUES
    # =========================================================================
    
    def __repr__(self) -> str:
        """Représentation string du modèle"""
        return (
            f"<Biome(id={self.id}, name='{self.name}', "
            f"multiplier={self.gathering_multiplier})>"
        )
    
    def __str__(self) -> str:
        """String lisible pour affichage"""
        return f"{self.name} (Gathering: {self.gathering_bonus_percent:+.0f}%, {self.resources_count} ressources)"