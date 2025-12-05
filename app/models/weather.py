# app/models/weather.py

from sqlalchemy import Column, Integer, String, Text, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from datetime import datetime
from typing import Dict, Any

from database import Base


class Weather(Base):
    """
    Modèle pour la table weathers
    
    Représente les conditions météorologiques qui affectent
    les multiplicateurs de gathering et crafting.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    __tablename__ = "weathers"
    
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
        doc="Multiplicateur pour le gathering (0.5 = -50%, 1.5 = +50%)"
    )
    crafting_multiplier = Column(
        Numeric(5, 2), 
        nullable=False, 
        default=1.00,
        doc="Multiplicateur pour le crafting"
    )
    duration_minutes = Column(
        Integer, 
        nullable=False, 
        default=60,
        doc="Durée moyenne de cette météo en minutes"
    )
    created_at = Column(
        "created_at",
        nullable=False,
        default=datetime.utcnow,
        doc="Date de création de l'enregistrement"
    )
    
    # =========================================================================
    # CONTRAINTES
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            'gathering_multiplier >= 0',
            name='chk_weathers_gathering_multiplier'
        ),
        CheckConstraint(
            'crafting_multiplier >= 0',
            name='chk_weathers_crafting_multiplier'
        ),
        CheckConstraint(
            'duration_minutes > 0',
            name='chk_weathers_duration'
        ),
    )
    
    # =========================================================================
    # RELATIONS
    # =========================================================================
    
    # Relation many-to-many avec resources via resources_weathers
    resources = relationship(
        "Resource",
        secondary="resources_weathers",
        back_populates="weathers",
        doc="Ressources affectées par cette météo"
    )
    
    # =========================================================================
    # PROPRIÉTÉS CALCULÉES
    # =========================================================================
    
    @property
    def is_favorable_for_gathering(self) -> bool:
        """
        Vérifie si la météo est favorable pour le gathering
        
        Returns:
            bool: True si multiplicateur > 1.0
        """
        return float(self.gathering_multiplier) > 1.0
    
    @property
    def is_favorable_for_crafting(self) -> bool:
        """
        Vérifie si la météo est favorable pour le crafting
        
        Returns:
            bool: True si multiplicateur > 1.0
        """
        return float(self.crafting_multiplier) > 1.0
    
    @property
    def gathering_bonus_percent(self) -> float:
        """
        Calcule le bonus/malus de gathering en pourcentage
        
        Returns:
            float: Pourcentage (ex: 20.0 pour +20%, -30.0 pour -30%)
        """
        return (float(self.gathering_multiplier) - 1.0) * 100
    
    @property
    def crafting_bonus_percent(self) -> float:
        """
        Calcule le bonus/malus de crafting en pourcentage
        
        Returns:
            float: Pourcentage
        """
        return (float(self.crafting_multiplier) - 1.0) * 100
    
    @property
    def overall_impact(self) -> str:
        """
        Évalue l'impact global de la météo
        
        Returns:
            str: "positive" | "negative" | "neutral" | "mixed"
        """
        gathering_bonus = float(self.gathering_multiplier) - 1.0
        crafting_bonus = float(self.crafting_multiplier) - 1.0
        
        if gathering_bonus > 0 and crafting_bonus > 0:
            return "positive"
        elif gathering_bonus < 0 and crafting_bonus < 0:
            return "negative"
        elif gathering_bonus == 0 and crafting_bonus == 0:
            return "neutral"
        else:
            return "mixed"
    
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
    
    def apply_crafting_multiplier(self, base_time: int) -> int:
        """
        Applique le multiplicateur de crafting au temps de base
        
        Args:
            base_time: Temps de craft de base (secondes)
            
        Returns:
            int: Temps ajusté (arrondi à l'entier supérieur)
        """
        adjusted_time = base_time / float(self.crafting_multiplier)
        return max(1, int(adjusted_time))  # Minimum 1 seconde
    
    def get_affected_resources_count(self) -> int:
        """
        Compte le nombre de ressources affectées par cette météo
        
        Returns:
            int: Nombre de ressources liées
        """
        return len(self.resources) if self.resources else 0
    
    # =========================================================================
    # SÉRIALISATION
    # =========================================================================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit le modèle en dictionnaire
        
        Args:
            include_relations: Inclure les relations (ressources)
            
        Returns:
            Dict: Représentation dictionnaire du modèle
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "gathering_multiplier": float(self.gathering_multiplier),
            "crafting_multiplier": float(self.crafting_multiplier),
            "duration_minutes": self.duration_minutes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Propriétés calculées
            "is_favorable_for_gathering": self.is_favorable_for_gathering,
            "is_favorable_for_crafting": self.is_favorable_for_crafting,
            "gathering_bonus_percent": self.gathering_bonus_percent,
            "crafting_bonus_percent": self.crafting_bonus_percent,
            "overall_impact": self.overall_impact
        }
        
        if include_relations and self.resources:
            data["resources_count"] = len(self.resources)
            data["resources"] = [
                {"id": r.id, "name": r.name} 
                for r in self.resources
            ]
        
        return data
    
    # =========================================================================
    # MÉTHODES MAGIQUES
    # =========================================================================
    
    def __repr__(self) -> str:
        """Représentation string du modèle"""
        return (
            f"<Weather(id={self.id}, name='{self.name}', "
            f"gathering={self.gathering_multiplier}, "
            f"crafting={self.crafting_multiplier})>"
        )
    
    def __str__(self) -> str:
        """String lisible pour affichage"""
        return f"{self.name} (Gathering: {self.gathering_bonus_percent:+.0f}%, Crafting: {self.crafting_bonus_percent:+.0f}%)"