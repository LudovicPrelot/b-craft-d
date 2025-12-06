"""
Module: models.market
"""

from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, TIMESTAMP, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from database import Base


class Market(Base):
    """
    Modèle pour la table markets (partitionnée par date)
    
    Représente une offre de vente sur le marché.
    Un vendeur met en vente une ressource à un certain prix.
    Les acheteurs peuvent acheter l'offre si elle est active.
    
    Attributes:
        id (int): Identifiant unique
        seller_id (int): ID du vendeur
        buyer_id (int): ID de l'acheteur (NULL si non vendu)
        resource_id (int): Ressource vendue
        quantity (int): Quantité en vente
        unit_price (int): Prix unitaire (en centièmes)
        status_id (int): Statut de l'offre (1=active, 2=sold, etc.)
        expires_at (datetime): Date d'expiration (NULL = pas d'expiration)
        created_at (datetime): Date de création
        updated_at (datetime): Date de dernière modification
    
    Relations:
        seller: Utilisateur vendeur
        buyer: Utilisateur acheteur (si vendu)
        resource: Ressource vendue
        status: Statut de l'offre
    
    Partitionnement:
        - Partitionné par RANGE sur created_at
        - Partitions: 2024, 2025, 2026, future
        - Améliore performances sur requêtes par date
    """
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "markets"
    
    # Colonnes principales
    id = Column(Integer, primary_key=True, index=True)
    
    # Acteurs
    seller_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    buyer_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Ressource
    resource_id = Column(
        Integer,
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Transaction
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)  # Centièmes (150 = 1.50)
    
    # Statut
    status_id = Column(
        Integer,
        ForeignKey("market_status.id", ondelete="RESTRICT"),
        nullable=False,
        default=1,  # Active
        index=True
    )
    
    # Dates
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('quantity <= 10000', name='check_quantity_max'),
        CheckConstraint('unit_price > 0', name='check_unit_price_positive'),
        CheckConstraint('seller_id != buyer_id', name='check_no_self_trading'),
        # Index composite pour recherche optimisée
        Index(
            'idx_markets_search',
            'resource_id',
            'status_id',
            'created_at',
            postgresql_where=(Column('status_id') == 1)  # Active seulement
        ),
    )
    
    # Relations
    seller = relationship(
        "User",
        foreign_keys=[seller_id],
        back_populates="sales",
        lazy="joined"
    )
    
    buyer = relationship(
        "User",
        foreign_keys=[buyer_id],
        back_populates="purchases",
        lazy="joined"
    )
    
    resource = relationship(
        "Resource",
        back_populates="market_listings",
        lazy="joined"
    )
    
    status = relationship(
        "MarketStatus",
        back_populates="markets",
        lazy="joined"
    )
    
    # ==================== PROPRIÉTÉS CALCULÉES ====================
    
    @property
    def is_active(self) -> bool:
        """
        Vérifie si l'offre est active
        
        Returns:
            bool: True si status = active
        """
        return self.status_id == 1
    
    @property
    def is_expired(self) -> bool:
        """
        Vérifie si l'offre a expiré
        
        Returns:
            bool: True si expires_at est dépassé
        """
        if not self.expires_at:
            return False
        return datetime.now(self.expires_at.tzinfo) > self.expires_at
    
    @property
    def is_sold(self) -> bool:
        """
        Vérifie si l'offre a été vendue
        
        Returns:
            bool: True si status = sold
        """
        return self.status_id == 2
    
    @property
    def is_cancelled(self) -> bool:
        """
        Vérifie si l'offre a été annulée
        
        Returns:
            bool: True si status = cancelled
        """
        return self.status_id == 3
    
    @property
    def unit_price_float(self) -> float:
        """
        Convertit le prix unitaire en float
        
        Returns:
            float: Prix unitaire (150 -> 1.50)
        """
        return self.unit_price / 100.0
    
    @property
    def total_price(self) -> float:
        """
        Calcule le prix total de l'offre
        
        Returns:
            float: quantity * unit_price
        """
        return round(self.quantity * self.unit_price_float, 2)
    
    @property
    def time_remaining(self) -> Optional[timedelta]:
        """
        Calcule le temps restant avant expiration
        
        Returns:
            timedelta: Temps restant ou None si pas d'expiration
        """
        if not self.expires_at:
            return None
        
        now = datetime.now(self.expires_at.tzinfo)
        if now >= self.expires_at:
            return timedelta(0)
        
        return self.expires_at - now
    
    @property
    def time_remaining_str(self) -> str:
        """
        Formate le temps restant en string lisible
        
        Returns:
            str: "2j 5h 30m" ou "Pas d'expiration" ou "Expiré"
        """
        if not self.expires_at:
            return "Pas d'expiration"
        
        remaining = self.time_remaining
        if not remaining or remaining.total_seconds() <= 0:
            return "Expiré"
        
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}j")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or not parts:
            parts.append(f"{minutes}m")
        
        return " ".join(parts)
    
    @property
    def seller_name(self) -> str:
        """Retourne le nom du vendeur"""
        return self.seller.login if self.seller else "Unknown"
    
    @property
    def buyer_name(self) -> Optional[str]:
        """Retourne le nom de l'acheteur"""
        return self.buyer.login if self.buyer else None
    
    @property
    def resource_name(self) -> str:
        """Retourne le nom de la ressource"""
        return self.resource.name if self.resource else "Unknown"
    
    @property
    def status_name(self) -> str:
        """Retourne le nom du statut"""
        return self.status.name if self.status else "unknown"
    
    # ==================== MÉTHODES DE VALIDATION ====================
    
    def can_buy(self, user_id: int) -> tuple[bool, Optional[str]]:
        """
        Vérifie si un utilisateur peut acheter cette offre
        
        Args:
            user_id (int): ID de l'utilisateur acheteur
        
        Returns:
            tuple[bool, str]: (peut_acheter, raison_si_non)
        """
        # Vérifier que ce n'est pas le vendeur
        if user_id == self.seller_id:
            return False, "Vous ne pouvez pas acheter votre propre offre"
        
        # Vérifier le statut
        if not self.is_active:
            return False, f"Cette offre n'est pas active (statut: {self.status_name})"
        
        # Vérifier l'expiration
        if self.is_expired:
            return False, "Cette offre a expiré"
        
        return True, None
    
    def can_cancel(self, user_id: int) -> tuple[bool, Optional[str]]:
        """
        Vérifie si un utilisateur peut annuler cette offre
        
        Args:
            user_id (int): ID de l'utilisateur
        
        Returns:
            tuple[bool, str]: (peut_annuler, raison_si_non)
        """
        # Vérifier que c'est le vendeur
        if user_id != self.seller_id:
            return False, "Seul le vendeur peut annuler cette offre"
        
        # Vérifier le statut
        if not self.status.can_cancel:
            return False, f"Cette offre ne peut pas être annulée (statut: {self.status_name})"
        
        return True, None
    
    # ==================== MÉTHODES MÉTIER ====================
    
    def complete_purchase(self, buyer_id: int, session) -> tuple[bool, Optional[str]]:
        """
        Complète l'achat de cette offre
        
        Cette méthode:
        1. Vérifie que l'achat est possible
        2. Transfère l'argent (seller.gold += total_price)
        3. Transfère les items (buyer.inventory += resource)
        4. Met à jour le statut à "sold"
        5. Enregistre l'acheteur
        
        Args:
            buyer_id (int): ID de l'acheteur
            session: Session SQLAlchemy
        
        Returns:
            tuple[bool, str]: (succès, message_erreur_si_échec)
        """
        # Vérifier que l'achat est possible
        can_buy, reason = self.can_buy(buyer_id)
        if not can_buy:
            return False, reason
        
        # Récupérer buyer et seller
        from models.user import User
        buyer = session.query(User).filter(User.id == buyer_id).first()
        
        if not buyer:
            return False, "Acheteur introuvable"
        
        # Vérifier que l'acheteur a assez d'argent
        if buyer.gold < self.total_price:
            return False, f"Fonds insuffisants (requis: {self.total_price}, disponible: {buyer.gold})"
        
        # Transaction: transférer l'argent
        buyer.gold -= self.total_price
        self.seller.gold += self.total_price
        
        # Transaction: transférer les items (géré par trigger SQL)
        # Le trigger trg_complete_market_transaction gère l'inventaire
        
        # Mettre à jour le statut
        self.status_id = 2  # SOLD
        self.buyer_id = buyer_id
        self.updated_at = func.now()
        
        return True, None
    
    def cancel(self, user_id: int, session) -> tuple[bool, Optional[str]]:
        """
        Annule cette offre
        
        Cette méthode:
        1. Vérifie que l'annulation est possible
        2. Retourne les items au vendeur (trigger SQL)
        3. Met à jour le statut à "cancelled"
        
        Args:
            user_id (int): ID de l'utilisateur qui annule
            session: Session SQLAlchemy
        
        Returns:
            tuple[bool, str]: (succès, message_erreur_si_échec)
        """
        # Vérifier que l'annulation est possible
        can_cancel, reason = self.can_cancel(user_id)
        if not can_cancel:
            return False, reason
        
        # Mettre à jour le statut
        self.status_id = 3  # CANCELLED
        self.updated_at = func.now()
        
        # Les items sont retournés par trigger SQL
        
        return True, None
    
    def mark_expired(self, session) -> bool:
        """
        Marque cette offre comme expirée
        
        Cette méthode est appelée automatiquement par le trigger
        trg_auto_expire_listings ou manuellement par un job cron.
        
        Args:
            session: Session SQLAlchemy
        
        Returns:
            bool: True si marqué expiré, False si déjà expiré
        """
        if self.status_id == 4:  # Déjà expiré
            return False
        
        if not self.is_active:  # Ne peut expirer que si active
            return False
        
        self.status_id = 4  # EXPIRED
        self.updated_at = func.now()
        
        return True
    
    def extend_expiration(self, hours: int) -> None:
        """
        Prolonge la durée de l'offre
        
        Args:
            hours (int): Nombre d'heures à ajouter
        """
        if not self.expires_at:
            # Si pas d'expiration, créer une
            self.expires_at = datetime.now() + timedelta(hours=hours)
        else:
            self.expires_at += timedelta(hours=hours)
        
        self.updated_at = func.now()
    
    # ==================== MÉTHODES STATIQUES ====================
    
    @staticmethod
    def get_active_listings(session, resource_id: Optional[int] = None, limit: int = 50):
        """
        Récupère les offres actives
        
        Args:
            session: Session SQLAlchemy
            resource_id (int): Filtrer par ressource (optionnel)
            limit (int): Nombre maximum de résultats
        
        Returns:
            list[Market]: Liste des offres actives
        """
        query = session.query(Market).filter(Market.status_id == 1)
        
        if resource_id:
            query = query.filter(Market.resource_id == resource_id)
        
        query = query.order_by(Market.created_at.desc()).limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_user_sales(session, user_id: int, include_inactive: bool = False):
        """
        Récupère les ventes d'un utilisateur
        
        Args:
            session: Session SQLAlchemy
            user_id (int): ID de l'utilisateur
            include_inactive (bool): Inclure offres non-actives
        
        Returns:
            list[Market]: Liste des ventes
        """
        query = session.query(Market).filter(Market.seller_id == user_id)
        
        if not include_inactive:
            query = query.filter(Market.status_id == 1)
        
        query = query.order_by(Market.created_at.desc())
        
        return query.all()
    
    @staticmethod
    def get_user_purchases(session, user_id: int):
        """
        Récupère les achats d'un utilisateur
        
        Args:
            session: Session SQLAlchemy
            user_id (int): ID de l'utilisateur
        
        Returns:
            list[Market]: Liste des achats
        """
        return session.query(Market).filter(
            Market.buyer_id == user_id,
            Market.status_id == 2  # SOLD
        ).order_by(Market.updated_at.desc()).all()
    
    # ==================== SÉRIALISATION ====================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit l'offre en dictionnaire
        
        Args:
            include_relations (bool): Inclure les détails des relations
        
        Returns:
            dict: Représentation JSON de l'offre
        """
        data = {
            "id": self.id,
            "seller_id": self.seller_id,
            "buyer_id": self.buyer_id,
            "resource_id": self.resource_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price_float,
            "total_price": self.total_price,
            "status_id": self.status_id,
            "status_name": self.status_name,
            "is_active": self.is_active,
            "is_expired": self.is_expired,
            "is_sold": self.is_sold,
            "is_cancelled": self.is_cancelled,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "time_remaining": self.time_remaining_str,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_relations:
            data["seller"] = {
                "id": self.seller.id,
                "login": self.seller.login
            } if self.seller else None
            
            data["buyer"] = {
                "id": self.buyer.id,
                "login": self.buyer.login
            } if self.buyer else None
            
            data["resource"] = {
                "id": self.resource.id,
                "name": self.resource.name,
                "icon": self.resource.icon
            } if self.resource else None
            
            data["status"] = self.status.to_dict() if self.status else None
        
        return data
    
    def __repr__(self) -> str:
        """Représentation string de l'offre"""
        return (
            f"<Market(id={self.id}, "
            f"seller='{self.seller_name}', "
            f"resource='{self.resource_name}', "
            f"quantity={self.quantity}, "
            f"price={self.total_price}, "
            f"status='{self.status_name}')>"
        )