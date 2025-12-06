# app/models/user_subclass.py

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from datetime import datetime, timedelta
from typing import Dict, Any

from database import Base


class UserSubclass(Base):
    """
    Modèle pour la table users_subclasses
    
    Représente le déblocage d'une sous-classe par un utilisateur.
    Table de liaison (many-to-many) entre users et subclasses.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    __tablename__ = "users_subclasses"
    
    # =========================================================================
    # COLONNES
    # =========================================================================
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        doc="ID de l'utilisateur"
    )
    subclass_id = Column(
        Integer, 
        ForeignKey('subclasses.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        doc="ID de la sous-classe débloquée"
    )
    unlocked_at = Column(
        "unlocked_at",
        nullable=False,
        default=datetime.utcnow,
        doc="Date et heure du déblocage"
    )
    
    # =========================================================================
    # CONTRAINTES
    # =========================================================================
    
    __table_args__ = (
        UniqueConstraint('user_id', 'subclass_id', name='uq_users_subclasses'),
    )
    
    # =========================================================================
    # RELATIONS
    # =========================================================================
    
    # Relation many-to-one avec user
    user = relationship(
        "User",
        back_populates="user_subclasses",
        doc="Utilisateur ayant débloqué la sous-classe"
    )
    
    # Relation many-to-one avec subclass
    subclass = relationship(
        "Subclass",
        back_populates="user_subclasses",
        doc="Sous-classe débloquée"
    )
    
    # =========================================================================
    # PROPRIÉTÉS CALCULÉES
    # =========================================================================
    
    @property
    def days_since_unlock(self) -> int:
        """
        Calcule le nombre de jours depuis le déblocage
        
        Returns:
            int: Jours écoulés
        """
        if not self.unlocked_at:
            return 0
        delta = datetime.utcnow() - self.unlocked_at
        return delta.days
    
    @property
    def is_recent(self) -> bool:
        """
        Vérifie si le déblocage est récent (< 7 jours)
        
        Returns:
            bool: True si déblocage récent
        """
        return self.days_since_unlock < 7
    
    @property
    def subclass_name(self) -> str:
        """
        Récupère le nom de la sous-classe
        
        Returns:
            str: Nom de la sous-classe ou "Inconnue"
        """
        if self.subclass:
            return self.subclass.name
        return "Inconnue"
    
    @property
    def profession_name(self) -> str:
        """
        Récupère le nom de la profession parente
        
        Returns:
            str: Nom de la profession
        """
        if self.subclass and self.subclass.profession:
            return self.subclass.profession.name
        return "Inconnue"
    
    @property
    def bonus_description(self) -> str:
        """
        Description du bonus de la sous-classe
        
        Returns:
            str: Description formatée
        """
        if self.subclass:
            return self.subclass.get_bonus_description()
        return "Aucun bonus"
    
    # =========================================================================
    # MÉTHODES MÉTIER
    # =========================================================================
    
    def apply_bonus(self, base_value: float) -> float:
        """
        Applique le bonus de la sous-classe à une valeur
        
        Args:
            base_value: Valeur de base
            
        Returns:
            float: Valeur avec bonus appliqué
        """
        if self.subclass:
            return self.subclass.apply_bonus(base_value)
        return base_value
    
    def is_applicable_for(self, profession_id: int) -> bool:
        """
        Vérifie si la sous-classe s'applique à une profession
        
        Args:
            profession_id: ID de la profession à vérifier
            
        Returns:
            bool: True si la sous-classe correspond
        """
        if not self.subclass:
            return False
        return self.subclass.profession_id == profession_id
    
    def get_achievement_data(self) -> Dict[str, Any]:
        """
        Génère les données pour un achievement de déblocage
        
        Returns:
            Dict: Données achievement
        """
        return {
            "achievement_type": "subclass_unlock",
            "subclass_id": self.subclass_id,
            "subclass_name": self.subclass_name,
            "profession_name": self.profession_name,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "is_recent": self.is_recent
        }
    
    @staticmethod
    def create_unlock(db_session, user_id: int, subclass_id: int) -> 'UserSubclass':
        """
        Crée un déblocage de sous-classe
        
        Args:
            db_session: Session SQLAlchemy
            user_id: ID de l'utilisateur
            subclass_id: ID de la sous-classe
            
        Returns:
            UserSubclass: Instance créée
            
        Raises:
            ValueError: Si déjà débloquée ou conditions non remplies
        """
        # Vérifier si déjà débloquée
        existing = db_session.query(UserSubclass).filter(
            UserSubclass.user_id == user_id,
            UserSubclass.subclass_id == subclass_id
        ).first()
        
        if existing:
            raise ValueError("Sous-classe déjà débloquée")
        
        # Vérifier les conditions (niveau, etc.)
        from models.subclass import Subclass
        subclass = db_session.query(Subclass).get(subclass_id)
        
        if not subclass or not subclass.is_active:
            raise ValueError("Sous-classe invalide ou inactive")
        
        # Créer le déblocage
        unlock = UserSubclass(
            user_id=user_id,
            subclass_id=subclass_id,
            unlocked_at=datetime.utcnow()
        )
        
        db_session.add(unlock)
        return unlock
    
    @staticmethod
    def get_user_subclasses_for_profession(
        db_session, 
        user_id: int, 
        profession_id: int
    ) -> list:
        """
        Récupère toutes les sous-classes débloquées pour une profession
        
        Args:
            db_session: Session SQLAlchemy
            user_id: ID de l'utilisateur
            profession_id: ID de la profession
            
        Returns:
            list: Liste des UserSubclass
        """
        from models.subclass import Subclass
        
        return db_session.query(UserSubclass).join(Subclass).filter(
            UserSubclass.user_id == user_id,
            Subclass.profession_id == profession_id
        ).all()
    
    @staticmethod
    def count_user_subclasses(db_session, user_id: int) -> int:
        """
        Compte le nombre total de sous-classes débloquées
        
        Args:
            db_session: Session SQLAlchemy
            user_id: ID de l'utilisateur
            
        Returns:
            int: Nombre de sous-classes
        """
        return db_session.query(UserSubclass).filter(
            UserSubclass.user_id == user_id
        ).count()
    
    # =========================================================================
    # SÉRIALISATION
    # =========================================================================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit le modèle en dictionnaire
        
        Args:
            include_relations: Inclure les relations (user, subclass)
            
        Returns:
            Dict: Représentation dictionnaire du modèle
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "subclass_id": self.subclass_id,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            # Propriétés calculées
            "days_since_unlock": self.days_since_unlock,
            "is_recent": self.is_recent,
            "subclass_name": self.subclass_name,
            "profession_name": self.profession_name,
            "bonus_description": self.bonus_description
        }
        
        if include_relations:
            if self.user:
                data["user"] = {
                    "id": self.user.id,
                    "login": self.user.login
                }
            
            if self.subclass:
                data["subclass"] = self.subclass.to_dict()
        
        return data
    
    # =========================================================================
    # MÉTHODES MAGIQUES
    # =========================================================================
    
    def __repr__(self) -> str:
        """Représentation string du modèle"""
        return (
            f"<UserSubclass(user_id={self.user_id}, subclass_id={self.subclass_id}, "
            f"unlocked_at='{self.unlocked_at}')>"
        )
    
    def __str__(self) -> str:
        """String lisible pour affichage"""
        return f"{self.subclass_name} débloquée il y a {self.days_since_unlock} jours"