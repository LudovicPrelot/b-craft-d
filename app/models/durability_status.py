"""
Module: models.durability_status
"""

from sqlalchemy import Column, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from typing import Dict, Any, Optional
from database import Base


class DurabilityStatus(Base):
    """
    Modèle pour la table durability_status
    
    Représente les différents états de durabilité d'un atelier.
    Table de référence (seed data) avec 5 statuts possibles.
    
    Attributes:
        id (int): Identifiant unique (1-5)
        name (str): Nom du statut
        description (str): Description du statut
        min_percent (int): Pourcentage minimum (0-100)
        max_percent (int): Pourcentage maximum (0-100)
        color_code (str): Code couleur hex pour UI
        
    Relations:
        workshops: Liste des ateliers avec ce statut
    
    Statuts disponibles:
        1. broken     - 0%           - Cassé, inutilisable
        2. critical   - 1-24%        - État critique, réparation urgente
        3. poor       - 25-49%       - Mauvais état
        4. fair       - 50-74%       - État moyen
        5. good       - 75-99%       - Bon état
        6. excellent  - 100%         - État excellent
    """
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "durability_status"
    
    # Colonnes
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    min_percent = Column(Integer, nullable=False)
    max_percent = Column(Integer, nullable=False)
    color_code = Column(String(7), nullable=False, default="#6c757d")
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('min_percent >= 0', name='check_min_percent_valid'),
        CheckConstraint('max_percent <= 100', name='check_max_percent_valid'),
        CheckConstraint('min_percent <= max_percent', name='check_percent_range_valid'),
    )
    
    # Relations
    workshops = relationship(
        "Workshop",
        back_populates="durability_status",
        lazy="dynamic"
    )
    
    # ==================== CONSTANTES DE CLASSE ====================
    
    # IDs des statuts (pour usage dans le code)
    BROKEN = 1
    CRITICAL = 2
    POOR = 3
    FAIR = 4
    GOOD = 5
    EXCELLENT = 6
    
    # Mapping nom -> ID
    STATUS_MAP = {
        "broken": BROKEN,
        "critical": CRITICAL,
        "poor": POOR,
        "fair": FAIR,
        "good": GOOD,
        "excellent": EXCELLENT
    }
    
    # Mapping ID -> nom
    ID_TO_NAME = {
        BROKEN: "broken",
        CRITICAL: "critical",
        POOR: "poor",
        FAIR: "fair",
        GOOD: "good",
        EXCELLENT: "excellent"
    }
    
    # ==================== PROPRIÉTÉS CALCULÉES ====================
    
    @property
    def is_broken(self) -> bool:
        """
        Vérifie si ce statut représente un état cassé
        
        Returns:
            bool: True si statut = broken
        """
        return self.id == self.BROKEN
    
    @property
    def requires_repair(self) -> bool:
        """
        Vérifie si ce statut nécessite une réparation
        
        Returns:
            bool: True si broken, critical ou poor
        """
        return self.id in [self.BROKEN, self.CRITICAL, self.POOR]
    
    @property
    def is_optimal(self) -> bool:
        """
        Vérifie si ce statut est optimal
        
        Returns:
            bool: True si excellent ou good
        """
        return self.id in [self.EXCELLENT, self.GOOD]
    
    @property
    def workshops_count(self) -> int:
        """
        Compte le nombre d'ateliers avec ce statut
        
        Returns:
            int: Nombre d'ateliers
        """
        return self.workshops.count()
    
    @property
    def percent_range(self) -> str:
        """
        Retourne la plage de pourcentage en texte
        
        Returns:
            str: "0%", "1-24%", "50-74%", etc.
        """
        if self.min_percent == self.max_percent:
            return f"{self.min_percent}%"
        return f"{self.min_percent}-{self.max_percent}%"
    
    # ==================== MÉTHODES DE CLASSE ====================
    
    @classmethod
    def get_by_name(cls, session, name: str) -> Optional['DurabilityStatus']:
        """
        Récupère un statut par son nom
        
        Args:
            session: Session SQLAlchemy
            name (str): Nom du statut ("broken", "excellent", etc.)
        
        Returns:
            DurabilityStatus: Instance du statut ou None
        """
        return session.query(cls).filter(cls.name == name.lower()).first()
    
    @classmethod
    def get_by_percent(cls, session, percent: float) -> Optional['DurabilityStatus']:
        """
        Récupère le statut correspondant à un pourcentage de durabilité
        
        Args:
            session: Session SQLAlchemy
            percent (float): Pourcentage de durabilité (0.0-100.0)
        
        Returns:
            DurabilityStatus: Statut correspondant
        """
        # Arrondir pour éviter les problèmes de précision
        percent = round(percent, 2)
        
        return session.query(cls).filter(
            cls.min_percent <= percent,
            cls.max_percent >= percent
        ).first()
    
    @classmethod
    def get_id_by_name(cls, name: str) -> Optional[int]:
        """
        Récupère l'ID d'un statut par son nom
        
        Args:
            name (str): Nom du statut
        
        Returns:
            int: ID du statut ou None
        """
        return cls.STATUS_MAP.get(name.lower())
    
    @classmethod
    def get_name_by_id(cls, status_id: int) -> Optional[str]:
        """
        Récupère le nom d'un statut par son ID
        
        Args:
            status_id (int): ID du statut
        
        Returns:
            str: Nom du statut ou None
        """
        return cls.ID_TO_NAME.get(status_id)
    
    @classmethod
    def get_status_for_durability(cls, session, durability: int, max_durability: int) -> Optional['DurabilityStatus']:
        """
        Calcule et récupère le statut de durabilité approprié
        
        Args:
            session: Session SQLAlchemy
            durability (int): Durabilité actuelle
            max_durability (int): Durabilité maximale
        
        Returns:
            DurabilityStatus: Statut correspondant
        """
        if max_durability == 0:
            return cls.get_by_percent(session, 0)
        
        percent = (durability / max_durability) * 100
        return cls.get_by_percent(session, percent)
    
    # ==================== MÉTHODES MÉTIER ====================
    
    def get_icon(self) -> str:
        """
        Retourne une icône pour l'affichage UI
        
        Returns:
            str: Nom de l'icône (Font Awesome)
        """
        icon_map = {
            self.BROKEN: "fa-times-circle",
            self.CRITICAL: "fa-exclamation-triangle",
            self.POOR: "fa-exclamation-circle",
            self.FAIR: "fa-minus-circle",
            self.GOOD: "fa-check-circle",
            self.EXCELLENT: "fa-star"
        }
        return icon_map.get(self.id, "fa-question-circle")
    
    def get_repair_priority(self) -> int:
        """
        Retourne la priorité de réparation (1=urgent, 5=pas nécessaire)
        
        Returns:
            int: Niveau de priorité (1-5)
        """
        priority_map = {
            self.BROKEN: 1,      # Urgent
            self.CRITICAL: 2,    # Haute
            self.POOR: 3,        # Moyenne
            self.FAIR: 4,        # Basse
            self.GOOD: 5,        # Pas nécessaire
            self.EXCELLENT: 5    # Pas nécessaire
        }
        return priority_map.get(self.id, 3)
    
    def contains_percent(self, percent: float) -> bool:
        """
        Vérifie si un pourcentage est dans la plage de ce statut
        
        Args:
            percent (float): Pourcentage à vérifier (0.0-100.0)
        
        Returns:
            bool: True si dans la plage
        """
        return self.min_percent <= percent <= self.max_percent
    
    # ==================== SÉRIALISATION ====================
    
    def to_dict(self, include_stats: bool = False) -> Dict[str, Any]:
        """
        Convertit le statut en dictionnaire
        
        Args:
            include_stats (bool): Inclure les statistiques (nombre ateliers)
        
        Returns:
            dict: Représentation JSON du statut
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "min_percent": self.min_percent,
            "max_percent": self.max_percent,
            "percent_range": self.percent_range,
            "color_code": self.color_code,
            "is_broken": self.is_broken,
            "requires_repair": self.requires_repair,
            "is_optimal": self.is_optimal,
            "repair_priority": self.get_repair_priority(),
            "icon": self.get_icon()
        }
        
        if include_stats:
            data["workshops_count"] = self.workshops_count
        
        return data
    
    def __repr__(self) -> str:
        """Représentation string du statut"""
        return (
            f"<DurabilityStatus(id={self.id}, name='{self.name}', "
            f"range='{self.percent_range}')>"
        )