# app/models/season.py

from sqlalchemy import Column, Integer, String, Text, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from datetime import datetime
from typing import Dict, Any, Optional

from database import Base


class Season(Base):
    """
    Modèle pour la table seasons
    
    Représente les saisons de l'année qui affectent
    les multiplicateurs de gathering et crafting.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    __tablename__ = "seasons"
    
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
        doc="Multiplicateur pour le gathering"
    )
    crafting_multiplier = Column(
        Numeric(5, 2), 
        nullable=False, 
        default=1.00,
        doc="Multiplicateur pour le crafting"
    )
    start_month = Column(
        Integer, 
        nullable=False,
        doc="Mois de début (1-12)"
    )
    end_month = Column(
        Integer, 
        nullable=False,
        doc="Mois de fin (1-12)"
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
            name='chk_seasons_gathering_multiplier'
        ),
        CheckConstraint(
            'crafting_multiplier >= 0',
            name='chk_seasons_crafting_multiplier'
        ),
        CheckConstraint(
            'start_month >= 1 AND start_month <= 12',
            name='chk_seasons_start_month'
        ),
        CheckConstraint(
            'end_month >= 1 AND end_month <= 12',
            name='chk_seasons_end_month'
        ),
    )
    
    # =========================================================================
    # RELATIONS
    # =========================================================================
    
    # Relation many-to-many avec resources via resources_seasons
    resources = relationship(
        "Resource",
        secondary="resources_seasons",
        back_populates="seasons",
        doc="Ressources affectées par cette saison"
    )
    
    # =========================================================================
    # PROPRIÉTÉS CALCULÉES
    # =========================================================================
    
    @property
    def is_favorable_for_gathering(self) -> bool:
        """Vérifie si la saison est favorable pour le gathering"""
        return float(self.gathering_multiplier) > 1.0
    
    @property
    def is_favorable_for_crafting(self) -> bool:
        """Vérifie si la saison est favorable pour le crafting"""
        return float(self.crafting_multiplier) > 1.0
    
    @property
    def gathering_bonus_percent(self) -> float:
        """Calcule le bonus/malus de gathering en pourcentage"""
        return (float(self.gathering_multiplier) - 1.0) * 100
    
    @property
    def crafting_bonus_percent(self) -> float:
        """Calcule le bonus/malus de crafting en pourcentage"""
        return (float(self.crafting_multiplier) - 1.0) * 100
    
    @property
    def duration_months(self) -> int:
        """
        Calcule la durée de la saison en mois
        
        Gère les saisons qui chevauchent l'année (ex: Hiver 12→2)
        
        Returns:
            int: Nombre de mois de la saison
        """
        if self.end_month >= self.start_month:
            return self.end_month - self.start_month + 1
        else:
            # Saison qui chevauche l'année (ex: Hiver 12, 1, 2)
            return (12 - self.start_month + 1) + self.end_month
    
    # =========================================================================
    # MÉTHODES MÉTIER
    # =========================================================================
    
    def is_current_month(self, month: int) -> bool:
        """
        Vérifie si un mois donné appartient à cette saison
        
        Args:
            month: Numéro du mois (1-12)
            
        Returns:
            bool: True si le mois appartient à cette saison
        """
        if self.end_month >= self.start_month:
            # Saison normale (ex: Printemps 3-5)
            return self.start_month <= month <= self.end_month
        else:
            # Saison qui chevauche l'année (ex: Hiver 12, 1, 2)
            return month >= self.start_month or month <= self.end_month
    
    def apply_gathering_multiplier(self, base_amount: float) -> float:
        """
        Applique le multiplicateur de gathering à une quantité de base
        
        Args:
            base_amount: Quantité de base récoltée
            
        Returns:
            float: Quantité ajustée
        """
        return base_amount * float(self.gathering_multiplier)
    
    def apply_crafting_multiplier(self, base_time: int) -> int:
        """
        Applique le multiplicateur de crafting au temps de base
        
        Args:
            base_time: Temps de craft de base (secondes)
            
        Returns:
            int: Temps ajusté
        """
        adjusted_time = base_time / float(self.crafting_multiplier)
        return max(1, int(adjusted_time))
    
    @staticmethod
    def get_current_season(db_session, current_month: Optional[int] = None) -> Optional['Season']:
        """
        Récupère la saison actuelle basée sur le mois
        
        Args:
            db_session: Session SQLAlchemy
            current_month: Mois actuel (1-12), ou None pour utiliser datetime.now()
            
        Returns:
            Season: Saison actuelle ou None
        """
        if current_month is None:
            current_month = datetime.now().month
        
        # Vérifier chaque saison
        seasons = db_session.query(Season).all()
        for season in seasons:
            if season.is_current_month(current_month):
                return season
        
        return None
    
    @staticmethod
    def get_season_by_name(db_session, name: str) -> Optional['Season']:
        """
        Récupère une saison par son nom
        
        Args:
            db_session: Session SQLAlchemy
            name: Nom de la saison
            
        Returns:
            Season: Saison trouvée ou None
        """
        return db_session.query(Season).filter(Season.name == name).first()
    
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
            "start_month": self.start_month,
            "end_month": self.end_month,
            "duration_months": self.duration_months,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Propriétés calculées
            "is_favorable_for_gathering": self.is_favorable_for_gathering,
            "is_favorable_for_crafting": self.is_favorable_for_crafting,
            "gathering_bonus_percent": self.gathering_bonus_percent,
            "crafting_bonus_percent": self.crafting_bonus_percent
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
            f"<Season(id={self.id}, name='{self.name}', "
            f"months={self.start_month}-{self.end_month})>"
        )
    
    def __str__(self) -> str:
        """String lisible pour affichage"""
        return f"{self.name} ({self.start_month}-{self.end_month}) - Gathering: {self.gathering_bonus_percent:+.0f}%"