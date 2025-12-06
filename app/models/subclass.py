# app/models/subclass.py

from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from datetime import datetime
from typing import Dict, Any, Optional

from database import Base


class Subclass(Base):
    """
    Modèle pour la table subclasses
    
    Représente les sous-classes (spécialisations) des professions
    débloquées à partir d'un certain niveau.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    __tablename__ = "subclasses"
    
    # =========================================================================
    # COLONNES
    # =========================================================================
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profession_id = Column(
        Integer, 
        ForeignKey('professions.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        doc="ID de la profession parente"
    )
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    unlock_level = Column(
        Integer, 
        nullable=False, 
        default=25,
        doc="Niveau de profession requis pour débloquer"
    )
    bonus_type = Column(
        String(50), 
        nullable=False,
        doc="Type de bonus (crafting_speed, gathering_yield, etc.)"
    )
    bonus_value = Column(
        Numeric(5, 2), 
        nullable=False, 
        default=0.00,
        doc="Valeur du bonus (0.10 = +10%)"
    )
    is_active = Column(
        Boolean, 
        nullable=False, 
        default=True,
        doc="Sous-classe active/disponible"
    )
    created_at = Column(
        "created_at",
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        "updated_at",
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # =========================================================================
    # CONTRAINTES
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            'unlock_level >= 1',
            name='chk_subclasses_unlock_level'
        ),
        CheckConstraint(
            'bonus_value >= 0',
            name='chk_subclasses_bonus_value'
        ),
    )
    
    # =========================================================================
    # RELATIONS
    # =========================================================================
    
    # Relation many-to-one avec profession
    profession = relationship(
        "Profession",
        back_populates="subclasses",
        doc="Profession parente de cette sous-classe"
    )
    
    # Relation many-to-many avec users via users_subclasses
    users = relationship(
        "User",
        secondary="users_subclasses",
        back_populates="subclasses",
        doc="Utilisateurs ayant débloqué cette sous-classe"
    )
    
    # =========================================================================
    # PROPRIÉTÉS CALCULÉES
    # =========================================================================
    
    @property
    def bonus_percent(self) -> float:
        """
        Convertit la valeur du bonus en pourcentage
        
        Returns:
            float: Bonus en pourcentage (ex: 15.0 pour +15%)
        """
        return float(self.bonus_value) * 100
    
    @property
    def full_name(self) -> str:
        """
        Nom complet avec profession parente
        
        Returns:
            str: Format "Profession - Sous-classe"
        """
        if self.profession:
            return f"{self.profession.name} - {self.name}"
        return self.name
    
    @property
    def is_unlockable(self) -> bool:
        """
        Vérifie si la sous-classe est débloquable (active)
        
        Returns:
            bool: True si active
        """
        return self.is_active
    
    @property
    def users_count(self) -> int:
        """
        Compte le nombre d'utilisateurs ayant cette sous-classe
        
        Returns:
            int: Nombre d'utilisateurs
        """
        return len(self.users) if self.users else 0
    
    # =========================================================================
    # MÉTHODES MÉTIER
    # =========================================================================
    
    def is_unlockable_by(self, user, db_session=None) -> bool:
        """
        Vérifie si un utilisateur peut débloquer cette sous-classe
        
        Args:
            user: Instance de User
            db_session: Session SQLAlchemy (optionnel)
            
        Returns:
            bool: True si l'utilisateur remplit les conditions
        """
        # Vérifier si sous-classe active
        if not self.is_active:
            return False
        
        # Vérifier si déjà débloquée
        if self.users and user in self.users:
            return False  # Déjà débloquée
        
        # Vérifier niveau de profession
        if hasattr(user, 'professions'):
            for user_profession in user.professions:
                if user_profession.profession_id == self.profession_id:
                    return user_profession.level >= self.unlock_level
        
        return False
    
    def has_user(self, user_id: int) -> bool:
        """
        Vérifie si un utilisateur a débloqué cette sous-classe
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: True si débloquée par cet utilisateur
        """
        if not self.users:
            return False
        return any(u.id == user_id for u in self.users)
    
    def apply_bonus(self, base_value: float) -> float:
        """
        Applique le bonus de la sous-classe à une valeur de base
        
        Args:
            base_value: Valeur de base
            
        Returns:
            float: Valeur avec bonus appliqué
        """
        return base_value * (1.0 + float(self.bonus_value))
    
    def get_bonus_description(self) -> str:
        """
        Génère une description lisible du bonus
        
        Returns:
            str: Description formatée (ex: "Crafting Speed +15%")
        """
        bonus_types = {
            "crafting_speed": "Vitesse de Crafting",
            "gathering_yield": "Rendement de Récolte",
            "success_rate": "Taux de Réussite",
            "xp_gain": "Gain d'XP",
            "durability_loss": "Usure Réduite",
            "quality_bonus": "Bonus de Qualité"
        }
        
        type_name = bonus_types.get(self.bonus_type, self.bonus_type.replace('_', ' ').title())
        sign = "+" if self.bonus_value > 0 else ""
        
        return f"{type_name} {sign}{self.bonus_percent:.0f}%"
    
    @staticmethod
    def get_available_for_user(db_session, user_id: int, profession_id: int) -> list:
        """
        Récupère les sous-classes disponibles pour un utilisateur
        
        Args:
            db_session: Session SQLAlchemy
            user_id: ID de l'utilisateur
            profession_id: ID de la profession
            
        Returns:
            list: Liste des sous-classes disponibles
        """
        # Import local pour éviter circular import
        from models.user_profession import UserProfession
        
        # Récupérer niveau de l'utilisateur dans cette profession
        user_prof = db_session.query(UserProfession).filter(
            UserProfession.user_id == user_id,
            UserProfession.profession_id == profession_id
        ).first()
        
        if not user_prof:
            return []
        
        # Récupérer sous-classes débloquables
        return db_session.query(Subclass).filter(
            Subclass.profession_id == profession_id,
            Subclass.is_active == True,
            Subclass.unlock_level <= user_prof.level
        ).all()
    
    # =========================================================================
    # SÉRIALISATION
    # =========================================================================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit le modèle en dictionnaire
        
        Args:
            include_relations: Inclure les relations (profession, users)
            
        Returns:
            Dict: Représentation dictionnaire du modèle
        """
        data = {
            "id": self.id,
            "profession_id": self.profession_id,
            "name": self.name,
            "description": self.description,
            "unlock_level": self.unlock_level,
            "bonus_type": self.bonus_type,
            "bonus_value": float(self.bonus_value),
            "bonus_percent": self.bonus_percent,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # Propriétés calculées
            "full_name": self.full_name,
            "is_unlockable": self.is_unlockable,
            "users_count": self.users_count,
            "bonus_description": self.get_bonus_description()
        }
        
        if include_relations:
            if self.profession:
                data["profession"] = {
                    "id": self.profession.id,
                    "name": self.profession.name,
                    "type": self.profession.type
                }
            
            if self.users:
                data["users"] = [
                    {"id": u.id, "login": u.login} 
                    for u in self.users[:10]  # Limiter à 10 pour performance
                ]
        
        return data
    
    # =========================================================================
    # MÉTHODES MAGIQUES
    # =========================================================================
    
    def __repr__(self) -> str:
        """Représentation string du modèle"""
        return (
            f"<Subclass(id={self.id}, name='{self.name}', "
            f"profession_id={self.profession_id}, unlock_level={self.unlock_level})>"
        )
    
    def __str__(self) -> str:
        """String lisible pour affichage"""
        return f"{self.full_name} (Niveau {self.unlock_level}) - {self.get_bonus_description()}"