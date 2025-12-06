"""
Module: models.market_status
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from typing import Dict, Any, Optional
from database import Base


class MarketStatus(Base):
    """
    Modèle pour la table market_status
    
    Représente les différents états d'une offre sur le marché.
    Table de référence (seed data) avec 5 statuts possibles.
    
    Attributes:
        id (int): Identifiant unique (1-5)
        name (str): Nom du statut
        description (str): Description du statut
    
    Relations:
        markets: Liste des offres avec ce statut
    
    Statuts disponibles:
        1. active - Offre active, achetable
        2. sold - Offre vendue avec succès
        3. cancelled - Offre annulée par le vendeur
        4. expired - Offre expirée (temps écoulé)
        5. reserved - Offre réservée temporairement
    """
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "market_status"
    
    # Colonnes
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    
    # Relations
    markets = relationship(
        "Market",
        back_populates="status",
        lazy="dynamic"
    )
    
    # ==================== CONSTANTES DE CLASSE ====================
    
    # IDs des statuts (pour usage dans le code)
    ACTIVE = 1
    SOLD = 2
    CANCELLED = 3
    EXPIRED = 4
    RESERVED = 5
    
    # Mapping nom -> ID
    STATUS_MAP = {
        "active": ACTIVE,
        "sold": SOLD,
        "cancelled": CANCELLED,
        "expired": EXPIRED,
        "reserved": RESERVED
    }
    
    # Mapping ID -> nom
    ID_TO_NAME = {
        ACTIVE: "active",
        SOLD: "sold",
        CANCELLED: "cancelled",
        EXPIRED: "expired",
        RESERVED: "reserved"
    }
    
    # ==================== PROPRIÉTÉS CALCULÉES ====================
    
    @property
    def is_active(self) -> bool:
        """
        Vérifie si ce statut représente une offre active
        
        Returns:
            bool: True si statut = active
        """
        return self.id == self.ACTIVE
    
    @property
    def is_final(self) -> bool:
        """
        Vérifie si ce statut est final (sold, cancelled, expired)
        
        Returns:
            bool: True si statut final (ne peut plus changer)
        """
        return self.id in [self.SOLD, self.CANCELLED, self.EXPIRED]
    
    @property
    def can_cancel(self) -> bool:
        """
        Vérifie si une offre avec ce statut peut être annulée
        
        Returns:
            bool: True si annulable (active ou reserved)
        """
        return self.id in [self.ACTIVE, self.RESERVED]
    
    @property
    def can_buy(self) -> bool:
        """
        Vérifie si une offre avec ce statut peut être achetée
        
        Returns:
            bool: True si achetable (active uniquement)
        """
        return self.id == self.ACTIVE
    
    @property
    def markets_count(self) -> int:
        """
        Compte le nombre d'offres avec ce statut
        
        Returns:
            int: Nombre d'offres
        """
        return self.markets.count()
    
    # ==================== MÉTHODES DE CLASSE ====================
    
    @classmethod
    def get_by_name(cls, session, name: str) -> Optional['MarketStatus']:
        """
        Récupère un statut par son nom
        
        Args:
            session: Session SQLAlchemy
            name (str): Nom du statut ("active", "sold", etc.)
        
        Returns:
            MarketStatus: Instance du statut ou None
        """
        return session.query(cls).filter(cls.name == name.lower()).first()
    
    @classmethod
    def get_active_status(cls, session) -> Optional['MarketStatus']:
        """
        Récupère le statut "active"
        
        Args:
            session: Session SQLAlchemy
        
        Returns:
            MarketStatus: Statut active
        """
        return session.query(cls).filter(cls.id == cls.ACTIVE).first()
    
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
    def is_valid_transition(cls, from_status: int, to_status: int) -> bool:
        """
        Vérifie si une transition de statut est valide
        
        Règles de transition:
        - active -> sold, cancelled, expired, reserved
        - reserved -> active, sold, cancelled
        - sold, cancelled, expired -> aucune transition (final)
        
        Args:
            from_status (int): Statut actuel
            to_status (int): Statut cible
        
        Returns:
            bool: True si transition valide
        """
        # Statuts finaux ne peuvent pas changer
        if from_status in [cls.SOLD, cls.CANCELLED, cls.EXPIRED]:
            return False
        
        # Transitions depuis active
        if from_status == cls.ACTIVE:
            return to_status in [cls.SOLD, cls.CANCELLED, cls.EXPIRED, cls.RESERVED]
        
        # Transitions depuis reserved
        if from_status == cls.RESERVED:
            return to_status in [cls.ACTIVE, cls.SOLD, cls.CANCELLED]
        
        return False
    
    # ==================== MÉTHODES MÉTIER ====================
    
    def get_color_code(self) -> str:
        """
        Retourne un code couleur pour l'affichage UI
        
        Returns:
            str: Code couleur hex (#RRGGBB)
        """
        color_map = {
            self.ACTIVE: "#28a745",      # Vert
            self.SOLD: "#6c757d",        # Gris
            self.CANCELLED: "#dc3545",   # Rouge
            self.EXPIRED: "#ffc107",     # Jaune
            self.RESERVED: "#17a2b8"     # Bleu
        }
        return color_map.get(self.id, "#6c757d")
    
    def get_icon(self) -> str:
        """
        Retourne une icône pour l'affichage UI
        
        Returns:
            str: Nom de l'icône (Font Awesome)
        """
        icon_map = {
            self.ACTIVE: "fa-check-circle",
            self.SOLD: "fa-handshake",
            self.CANCELLED: "fa-times-circle",
            self.EXPIRED: "fa-clock",
            self.RESERVED: "fa-lock"
        }
        return icon_map.get(self.id, "fa-question-circle")
    
    # ==================== SÉRIALISATION ====================
    
    def to_dict(self, include_stats: bool = False) -> Dict[str, Any]:
        """
        Convertit le statut en dictionnaire
        
        Args:
            include_stats (bool): Inclure les statistiques (nombre offres)
        
        Returns:
            dict: Représentation JSON du statut
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "is_final": self.is_final,
            "can_cancel": self.can_cancel,
            "can_buy": self.can_buy,
            "color_code": self.get_color_code(),
            "icon": self.get_icon()
        }
        
        if include_stats:
            data["markets_count"] = self.markets_count
        
        return data
    
    def __repr__(self) -> str:
        """Représentation string du statut"""
        return f"<MarketStatus(id={self.id}, name='{self.name}')>"