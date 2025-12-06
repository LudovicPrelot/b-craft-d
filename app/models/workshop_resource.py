"""
Module: models.workshop_resource
"""

from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from typing import Dict, Any
from database import Base


class WorkshopResource(Base):
    """
    Modèle pour la table workshops_resources (table d'association)
    
    Représente les ressources nécessaires pour construire un atelier.
    Chaque workshop nécessite plusieurs ressources en quantités spécifiques.
    
    Attributes:
        id (int): Identifiant unique
        workshop_id (int): Référence au workshop
        resource_id (int): Référence à la ressource
        quantity (int): Quantité nécessaire (1-1000)
    
    Relations:
        workshop: Workshop auquel appartient cette ressource
        resource: Ressource nécessaire
    
    Exemples:
        - Forge nécessite: 50 Minerai de Fer, 20 Charbon, 10 Pierre
        - Établi nécessite: 30 Bois de Chêne, 5 Clous en Fer
    """
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "workshops_resources"
    
    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    
    workshop_id = Column(
        Integer,
        ForeignKey("workshops.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    resource_id = Column(
        Integer,
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    quantity = Column(Integer, nullable=False, default=1)
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('quantity <= 1000', name='check_quantity_max'),
        UniqueConstraint(
            'workshop_id', 
            'resource_id', 
            name='unique_workshop_resource'
        ),
    )
    
    # Relations
    workshop = relationship(
        "Workshop",
        back_populates="resources",
        lazy="joined"
    )
    
    resource = relationship(
        "Resource",
        lazy="joined"
    )
    
    # ==================== PROPRIÉTÉS CALCULÉES ====================
    
    @property
    def total_cost(self) -> float:
        """
        Calcule le coût total de cette ressource
        
        Returns:
            float: quantity * resource.base_value
        """
        if not self.resource:
            return 0.0
        
        return round(self.quantity * self.resource.base_value, 2)
    
    @property
    def resource_name(self) -> str:
        """
        Retourne le nom de la ressource
        
        Returns:
            str: Nom de la ressource ou "Unknown"
        """
        return self.resource.name if self.resource else "Unknown"
    
    @property
    def workshop_name(self) -> str:
        """
        Retourne le nom du workshop
        
        Returns:
            str: Nom du workshop ou "Unknown"
        """
        return self.workshop.name if self.workshop else "Unknown"
    
    # ==================== MÉTHODES MÉTIER ====================
    
    def has_sufficient_quantity(self, available: int) -> bool:
        """
        Vérifie si la quantité disponible est suffisante
        
        Args:
            available (int): Quantité disponible dans l'inventaire
        
        Returns:
            bool: True si suffisant, False sinon
        """
        return available >= self.quantity
    
    def get_missing_quantity(self, available: int) -> int:
        """
        Calcule la quantité manquante
        
        Args:
            available (int): Quantité disponible dans l'inventaire
        
        Returns:
            int: Quantité manquante (0 si suffisant)
        """
        return max(0, self.quantity - available)
    
    def get_completion_percent(self, available: int) -> float:
        """
        Calcule le pourcentage de complétion
        
        Args:
            available (int): Quantité disponible dans l'inventaire
        
        Returns:
            float: Pourcentage (0.0 à 100.0)
        """
        if self.quantity == 0:
            return 100.0
        
        percent = (min(available, self.quantity) / self.quantity) * 100
        return round(percent, 2)
    
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
            "resource_id": self.resource_id,
            "quantity": self.quantity
        }
        
        if include_relations:
            if self.resource:
                data["resource"] = {
                    "id": self.resource.id,
                    "name": self.resource.name,
                    "base_value": self.resource.base_value,
                    "icon": self.resource.icon
                }
            
            if self.workshop:
                data["workshop"] = {
                    "id": self.workshop.id,
                    "name": self.workshop.name
                }
            
            data["total_cost"] = self.total_cost
        
        return data
    
    def __repr__(self) -> str:
        """Représentation string"""
        return (
            f"<WorkshopResource(id={self.id}, "
            f"workshop='{self.workshop_name}', "
            f"resource='{self.resource_name}', "
            f"quantity={self.quantity})>"
        )