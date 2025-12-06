"""
Module: models.workshop
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from typing import Optional, Dict, Any
from database import Base


class Workshop(Base):
    """
    Modèle pour la table workshops
    
    Représente un atelier de craft ou un outil utilisé par une profession.
    Possède une durabilité qui se dégrade à chaque utilisation
    et peut être réparé moyennant des ressources.
    
    Attributes:
        id (int): Identifiant unique
        name (str): Nom de l'atelier (ex: "Forge", "Établi")
        description (str): Description détaillée
        profession_id (int): Profession qui utilise cet atelier
        max_durability (int): Durabilité maximale (100-1000)
        durability (int): Durabilité actuelle
        repair_cost_multiplier (float): Multiplicateur coût réparation
        crafting_speed_bonus (float): Bonus vitesse craft (1.0 = normal, 1.5 = +50%)
    
    Relations:
        profession: Profession propriétaire
        resources: Ressources nécessaires à la construction
        biomes: Biomes où l'atelier peut être construit
    """
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "workshops"
    
    # Colonnes principales
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Référence profession
    profession_id = Column(
        Integer, 
        ForeignKey("professions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Durabilité
    max_durability = Column(Integer, nullable=False, default=500)
    durability = Column(Integer, nullable=False, default=500)
    
    # Caractéristiques
    repair_cost_multiplier = Column(
        Integer,  # Stocké en centièmes (150 = 1.50)
        nullable=False,
        default=100
    )
    crafting_speed_bonus = Column(
        Integer,  # Stocké en centièmes (150 = 1.50)
        nullable=False,
        default=100
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('max_durability >= 100', name='check_max_durability_min'),
        CheckConstraint('max_durability <= 1000', name='check_max_durability_max'),
        CheckConstraint('durability >= 0', name='check_durability_positive'),
        CheckConstraint('durability <= max_durability', name='check_durability_valid'),
        CheckConstraint('repair_cost_multiplier > 0', name='check_repair_cost_positive'),
        CheckConstraint('crafting_speed_bonus > 0', name='check_speed_bonus_positive'),
    )
    
    # Relations
    profession = relationship(
        "Profession",
        back_populates="workshops",
        lazy="joined"
    )
    
    resources = relationship(
        "WorkshopResource",
        back_populates="workshop",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    biomes = relationship(
        "WorkshopBiome",
        back_populates="workshop",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # ==================== PROPRIÉTÉS CALCULÉES ====================
    
    @property
    def is_broken(self) -> bool:
        """
        Vérifie si l'atelier est cassé (durabilité = 0)
        
        Returns:
            bool: True si cassé, False sinon
        """
        return self.durability == 0
    
    @property
    def durability_percent(self) -> float:
        """
        Calcule le pourcentage de durabilité restante
        
        Returns:
            float: Pourcentage (0.0 à 100.0)
        """
        if self.max_durability == 0:
            return 0.0
        return round((self.durability / self.max_durability) * 100, 2)
    
    @property
    def repair_cost_multiplier_float(self) -> float:
        """Convertit le multiplicateur en float (150 -> 1.50)"""
        return self.repair_cost_multiplier / 100.0
    
    @property
    def crafting_speed_bonus_float(self) -> float:
        """Convertit le bonus en float (150 -> 1.50)"""
        return self.crafting_speed_bonus / 100.0
    
    @property
    def durability_status(self) -> str:
        """
        Retourne le statut de durabilité en texte
        
        Returns:
            str: "Excellent", "Bon", "Moyen", "Mauvais", "Cassé"
        """
        percent = self.durability_percent
        
        if percent == 0:
            return "Cassé"
        elif percent < 25:
            return "Mauvais"
        elif percent < 50:
            return "Moyen"
        elif percent < 75:
            return "Bon"
        else:
            return "Excellent"
    
    # ==================== MÉTHODES MÉTIER ====================
    
    def use(self, amount: int = 5) -> bool:
        """
        Utilise l'atelier, réduisant sa durabilité
        
        Args:
            amount (int): Montant de durabilité à retirer (défaut: 5)
        
        Returns:
            bool: True si utilisé avec succès, False si cassé
        
        Raises:
            ValueError: Si amount est négatif ou nul
        """
        if amount <= 0:
            raise ValueError("Le montant d'usure doit être positif")
        
        if self.is_broken:
            return False
        
        # Réduire la durabilité (sans descendre sous 0)
        self.durability = max(0, self.durability - amount)
        
        return True
    
    def repair(self, full: bool = False) -> int:
        """
        Répare l'atelier
        
        Args:
            full (bool): Si True, répare complètement. Si False, répare 50%
        
        Returns:
            int: Montant de durabilité restaurée
        """
        old_durability = self.durability
        
        if full:
            # Réparation complète
            self.durability = self.max_durability
        else:
            # Réparation partielle (50% de la durabilité manquante)
            missing = self.max_durability - self.durability
            restore_amount = int(missing * 0.5)
            self.durability = min(self.max_durability, self.durability + restore_amount)
        
        return self.durability - old_durability
    
    def calculate_repair_cost(self, full: bool = False) -> float:
        """
        Calcule le coût de réparation
        
        Formule: (durabilité_manquante / durabilité_max) * 100 * multiplicateur
        
        Args:
            full (bool): Si True, calcule coût réparation complète
        
        Returns:
            float: Coût de réparation en pièces d'or
        """
        if full:
            missing = self.max_durability - self.durability
        else:
            missing = int((self.max_durability - self.durability) * 0.5)
        
        base_cost = (missing / self.max_durability) * 100
        final_cost = base_cost * self.repair_cost_multiplier_float
        
        return round(final_cost, 2)
    
    def can_craft(self) -> bool:
        """
        Vérifie si l'atelier peut être utilisé pour crafter
        
        Returns:
            bool: True si utilisable, False si cassé
        """
        return not self.is_broken
    
    def get_effective_craft_speed(self, base_time: int) -> int:
        """
        Calcule le temps de craft effectif avec bonus
        
        Args:
            base_time (int): Temps de craft de base en secondes
        
        Returns:
            int: Temps de craft avec bonus appliqué
        """
        if self.is_broken:
            return base_time  # Pas de bonus si cassé
        
        effective_time = base_time / self.crafting_speed_bonus_float
        return max(1, int(effective_time))  # Minimum 1 seconde
    
    # ==================== SÉRIALISATION ====================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit le workshop en dictionnaire
        
        Args:
            include_relations (bool): Inclure les relations (profession, resources, biomes)
        
        Returns:
            dict: Représentation JSON du workshop
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "profession_id": self.profession_id,
            "max_durability": self.max_durability,
            "durability": self.durability,
            "durability_percent": self.durability_percent,
            "durability_status": self.durability_status,
            "is_broken": self.is_broken,
            "repair_cost_multiplier": self.repair_cost_multiplier_float,
            "crafting_speed_bonus": self.crafting_speed_bonus_float,
            "repair_cost_full": self.calculate_repair_cost(full=True),
            "repair_cost_partial": self.calculate_repair_cost(full=False)
        }
        
        if include_relations:
            data["profession"] = {
                "id": self.profession.id,
                "name": self.profession.name
            } if self.profession else None
            
            data["required_resources"] = [
                {
                    "resource_id": wr.resource_id,
                    "quantity": wr.quantity
                }
                for wr in self.resources
            ]
            
            data["available_biomes"] = [
                {
                    "biome_id": wb.biome_id
                }
                for wb in self.biomes
            ]
        
        return data
    
    def __repr__(self) -> str:
        """Représentation string du workshop"""
        return (
            f"<Workshop(id={self.id}, name='{self.name}', "
            f"durability={self.durability}/{self.max_durability}, "
            f"status='{self.durability_status}')>"
        )