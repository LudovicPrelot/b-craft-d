"""
Module: models.device
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from database import Base


class Device(Base):
    """
    Modèle pour la table devices
    
    Représente un appareil connecté utilisé par un joueur.
    Utilisé pour la sécurité (détection appareils suspects),
    les statistiques (plateforme préférée) et la gestion des sessions.
    
    Attributes:
        id (int): Identifiant unique
        user_id (int): Référence à l'utilisateur
        device_name (str): Nom de l'appareil (ex: "iPhone 12", "Chrome Windows")
        device_type (str): Type d'appareil (mobile, desktop, tablet)
        os_name (str): Système d'exploitation (iOS, Android, Windows, etc.)
        os_version (str): Version de l'OS
        browser_name (str): Nom du navigateur (Chrome, Firefox, Safari, etc.)
        browser_version (str): Version du navigateur
        ip_address (str): Dernière adresse IP connue
        user_agent (str): User-Agent complet
        is_trusted (bool): Appareil de confiance
        last_used_at (datetime): Dernière utilisation
        created_at (datetime): Date de premier usage
        updated_at (datetime): Date de dernière modification
    
    Relations:
        user: Utilisateur propriétaire
    
    Notes:
        - Un utilisateur peut avoir plusieurs devices
        - Utilisé pour authentification multi-facteurs (MFA)
        - Permet de détecter connexions suspectes
    """
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "devices"
    
    # Colonnes principales
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Informations appareil
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(20), nullable=False, default="desktop")
    
    # Système d'exploitation
    os_name = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)
    
    # Navigateur
    browser_name = Column(String(50), nullable=True)
    browser_version = Column(String(50), nullable=True)
    
    # Réseau
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 max 45 chars
    user_agent = Column(String(500), nullable=True)
    
    # Sécurité
    is_trusted = Column(Boolean, nullable=False, default=False)
    
    # Dates
    last_used_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Index composites
    __table_args__ = (
        Index('idx_devices_user_last_used', 'user_id', 'last_used_at'),
        Index('idx_devices_trusted', 'user_id', 'is_trusted'),
    )
    
    # Relations
    user = relationship(
        "User",
        back_populates="devices",
        lazy="joined"
    )
    
    # ==================== PROPRIÉTÉS CALCULÉES ====================
    
    @property
    def is_mobile(self) -> bool:
        """
        Vérifie si c'est un appareil mobile
        
        Returns:
            bool: True si mobile ou tablet
        """
        return self.device_type in ["mobile", "tablet"]
    
    @property
    def is_desktop(self) -> bool:
        """
        Vérifie si c'est un ordinateur de bureau
        
        Returns:
            bool: True si desktop
        """
        return self.device_type == "desktop"
    
    @property
    def days_since_last_use(self) -> int:
        """
        Calcule le nombre de jours depuis la dernière utilisation
        
        Returns:
            int: Nombre de jours
        """
        delta = datetime.now(self.last_used_at.tzinfo) - self.last_used_at
        return delta.days
    
    @property
    def is_recently_used(self) -> bool:
        """
        Vérifie si l'appareil a été utilisé récemment (< 7 jours)
        
        Returns:
            bool: True si utilisé dans les 7 derniers jours
        """
        return self.days_since_last_use < 7
    
    @property
    def is_active(self) -> bool:
        """
        Vérifie si l'appareil est actif (< 30 jours)
        
        Returns:
            bool: True si utilisé dans les 30 derniers jours
        """
        return self.days_since_last_use < 30
    
    @property
    def full_os_name(self) -> str:
        """
        Retourne le nom complet de l'OS avec version
        
        Returns:
            str: "Windows 11", "iOS 17.1", etc.
        """
        if self.os_version:
            return f"{self.os_name} {self.os_version}"
        return self.os_name or "Unknown OS"
    
    @property
    def full_browser_name(self) -> str:
        """
        Retourne le nom complet du navigateur avec version
        
        Returns:
            str: "Chrome 120.0", "Safari 17.2", etc.
        """
        if self.browser_version:
            return f"{self.browser_name} {self.browser_version}"
        return self.browser_name or "Unknown Browser"
    
    @property
    def display_name(self) -> str:
        """
        Retourne un nom d'affichage lisible
        
        Returns:
            str: "iPhone 12 (iOS 17.1)" ou "Chrome (Windows 11)"
        """
        if self.device_name:
            return f"{self.device_name} ({self.full_os_name})"
        return f"{self.full_browser_name} ({self.full_os_name})"
    
    @property
    def trust_status(self) -> str:
        """
        Retourne le statut de confiance en texte
        
        Returns:
            str: "Trusted", "Untrusted"
        """
        return "Trusted" if self.is_trusted else "Untrusted"
    
    @property
    def activity_status(self) -> str:
        """
        Retourne le statut d'activité en texte
        
        Returns:
            str: "Active", "Recent", "Inactive"
        """
        days = self.days_since_last_use
        
        if days == 0:
            return "Active"
        elif days < 7:
            return "Recent"
        elif days < 30:
            return "Idle"
        else:
            return "Inactive"
    
    # ==================== MÉTHODES MÉTIER ====================
    
    def update_last_used(self, ip_address: Optional[str] = None) -> None:
        """
        Met à jour la date de dernière utilisation
        
        Args:
            ip_address (str): Nouvelle adresse IP (optionnel)
        """
        self.last_used_at = func.now()
        
        if ip_address:
            self.ip_address = ip_address
        
        self.updated_at = func.now()
    
    def mark_as_trusted(self) -> None:
        """Marque l'appareil comme de confiance"""
        self.is_trusted = True
        self.updated_at = func.now()
    
    def mark_as_untrusted(self) -> None:
        """Marque l'appareil comme non-fiable"""
        self.is_trusted = False
        self.updated_at = func.now()
    
    def update_info(
        self,
        device_name: Optional[str] = None,
        os_version: Optional[str] = None,
        browser_version: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Met à jour les informations de l'appareil
        
        Args:
            device_name (str): Nouveau nom d'appareil
            os_version (str): Nouvelle version OS
            browser_version (str): Nouvelle version navigateur
            ip_address (str): Nouvelle adresse IP
        """
        if device_name:
            self.device_name = device_name
        if os_version:
            self.os_version = os_version
        if browser_version:
            self.browser_version = browser_version
        if ip_address:
            self.ip_address = ip_address
        
        self.updated_at = func.now()
    
    def is_ip_changed(self, new_ip: str) -> bool:
        """
        Vérifie si l'adresse IP a changé
        
        Args:
            new_ip (str): Nouvelle adresse IP
        
        Returns:
            bool: True si IP différente
        """
        return self.ip_address != new_ip
    
    def should_reverify(self) -> bool:
        """
        Détermine si l'appareil nécessite une re-vérification
        
        Règles:
        - Non-fiable ET inactif > 30 jours
        - Non-fiable ET IP changée
        
        Returns:
            bool: True si re-vérification nécessaire
        """
        if self.is_trusted:
            return False
        
        # Inactif depuis longtemps
        if self.days_since_last_use > 30:
            return True
        
        return False
    
    def get_security_score(self) -> float:
        """
        Calcule un score de sécurité (0.0 = suspect, 1.0 = très sûr)
        
        Critères:
        - Appareil de confiance: +0.5
        - Utilisé récemment (< 7j): +0.2
        - Utilisé régulièrement (< 30j): +0.1
        - Desktop: +0.1
        - IP stable: +0.1
        
        Returns:
            float: Score de 0.0 à 1.0
        """
        score = 0.0
        
        if self.is_trusted:
            score += 0.5
        
        if self.days_since_last_use < 7:
            score += 0.2
        elif self.days_since_last_use < 30:
            score += 0.1
        
        if self.is_desktop:
            score += 0.1
        
        # IP stable (heuristique: même IP depuis 30+ jours)
        if self.days_since_last_use < 30 and self.ip_address:
            score += 0.1
        
        return round(min(score, 1.0), 2)
    
    # ==================== MÉTHODES STATIQUES ====================
    
    @staticmethod
    def get_user_devices(session, user_id: int, active_only: bool = False):
        """
        Récupère les appareils d'un utilisateur
        
        Args:
            session: Session SQLAlchemy
            user_id (int): ID de l'utilisateur
            active_only (bool): Uniquement les appareils actifs (< 30j)
        
        Returns:
            list[Device]: Liste des appareils
        """
        query = session.query(Device).filter(Device.user_id == user_id)
        
        if active_only:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            query = query.filter(Device.last_used_at > thirty_days_ago)
        
        return query.order_by(Device.last_used_at.desc()).all()
    
    @staticmethod
    def get_trusted_devices(session, user_id: int):
        """
        Récupère les appareils de confiance d'un utilisateur
        
        Args:
            session: Session SQLAlchemy
            user_id (int): ID de l'utilisateur
        
        Returns:
            list[Device]: Appareils de confiance
        """
        return session.query(Device).filter(
            Device.user_id == user_id,
            Device.is_trusted == True
        ).order_by(Device.last_used_at.desc()).all()
    
    @staticmethod
    def find_by_fingerprint(
        session,
        user_id: int,
        device_name: str,
        os_name: str,
        browser_name: str
    ) -> Optional['Device']:
        """
        Recherche un appareil par empreinte (fingerprint)
        
        Args:
            session: Session SQLAlchemy
            user_id (int): ID de l'utilisateur
            device_name (str): Nom de l'appareil
            os_name (str): Nom de l'OS
            browser_name (str): Nom du navigateur
        
        Returns:
            Device: Appareil trouvé ou None
        """
        return session.query(Device).filter(
            Device.user_id == user_id,
            Device.device_name == device_name,
            Device.os_name == os_name,
            Device.browser_name == browser_name
        ).first()
    
    # ==================== SÉRIALISATION ====================
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convertit l'appareil en dictionnaire
        
        Args:
            include_sensitive (bool): Inclure données sensibles (IP, user_agent)
        
        Returns:
            dict: Représentation JSON de l'appareil
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "display_name": self.display_name,
            "os_name": self.os_name,
            "os_version": self.os_version,
            "full_os_name": self.full_os_name,
            "browser_name": self.browser_name,
            "browser_version": self.browser_version,
            "full_browser_name": self.full_browser_name,
            "is_trusted": self.is_trusted,
            "trust_status": self.trust_status,
            "is_mobile": self.is_mobile,
            "is_desktop": self.is_desktop,
            "days_since_last_use": self.days_since_last_use,
            "is_recently_used": self.is_recently_used,
            "is_active": self.is_active,
            "activity_status": self.activity_status,
            "security_score": self.get_security_score(),
            "last_used_at": self.last_used_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data["ip_address"] = self.ip_address
            data["user_agent"] = self.user_agent
        
        return data
    
    def __repr__(self) -> str:
        """Représentation string de l'appareil"""
        return (
            f"<Device(id={self.id}, "
            f"user_id={self.user_id}, "
            f"name='{self.device_name}', "
            f"type='{self.device_type}', "
            f"trusted={self.is_trusted})>"
        )