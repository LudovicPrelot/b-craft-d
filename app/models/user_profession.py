# app/models/user_profession.py

from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from datetime import datetime
from typing import Dict, Any

from database import Base


class UserProfession(Base):
    """
    Modèle pour la table users_professions
    
    Représente la progression d'un utilisateur dans une profession spécifique.
    Version v3.0 avec mastery_rank_id et propriétés calculées avancées.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    __tablename__ = "users_professions"
    
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
    profession_id = Column(
        Integer, 
        ForeignKey('professions.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        doc="ID de la profession"
    )
    level = Column(
        Integer, 
        nullable=False, 
        default=1,
        doc="Niveau actuel dans cette profession"
    )
    experience = Column(
        Integer, 
        nullable=False, 
        default=0,
        doc="Points d'expérience actuels"
    )
    mastery_rank_id = Column(
        Integer, 
        ForeignKey('mastery_rank.id', ondelete='RESTRICT'),
        nullable=False,
        default=1,
        index=True,
        doc="ID du rang de maîtrise actuel (NEW v3.0)"
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
            'level >= 1',
            name='chk_users_professions_level'
        ),
        CheckConstraint(
            'experience >= 0',
            name='chk_users_professions_experience'
        ),
    )
    
    # =========================================================================
    # RELATIONS
    # =========================================================================
    
    # Relation many-to-one avec user
    user = relationship(
        "User",
        back_populates="professions",
        doc="Utilisateur possédant cette profession"
    )
    
    # Relation many-to-one avec profession
    profession = relationship(
        "Profession",
        back_populates="users",
        doc="Profession maîtrisée"
    )
    
    # Relation many-to-one avec mastery_rank (NEW v3.0)
    mastery_rank = relationship(
        "MasteryRank",
        back_populates="user_professions",
        doc="Rang de maîtrise actuel"
    )
    
    # =========================================================================
    # PROPRIÉTÉS CALCULÉES
    # =========================================================================
    
    @property
    def next_level_xp(self) -> int:
        """
        Calcule l'XP nécessaire pour le prochain niveau
        
        Formule: level * 100
        
        Returns:
            int: XP requis pour level up
        """
        return self.level * 100
    
    @property
    def progress_percent(self) -> float:
        """
        Calcule le pourcentage de progression vers le niveau suivant
        
        Returns:
            float: Pourcentage (0.0 à 100.0)
        """
        if self.next_level_xp == 0:
            return 0.0
        return (self.experience / self.next_level_xp) * 100.0
    
    @property
    def xp_remaining(self) -> int:
        """
        Calcule l'XP manquant pour le niveau suivant
        
        Returns:
            int: XP manquant
        """
        return max(0, self.next_level_xp - self.experience)
    
    @property
    def is_max_level(self) -> bool:
        """
        Vérifie si le niveau maximum est atteint
        
        Returns:
            bool: True si niveau max (basé sur profession.max_level)
        """
        if self.profession:
            return self.level >= self.profession.max_level
        return False
    
    @property
    def mastery_bonus_multiplier(self) -> float:
        """
        Récupère le multiplicateur du rang de maîtrise actuel
        
        Returns:
            float: Multiplicateur (1.0 à 2.0)
        """
        if self.mastery_rank:
            return float(self.mastery_rank.bonus_multiplier)
        return 1.0
    
    @property
    def mastery_rank_name(self) -> str:
        """
        Récupère le nom du rang de maîtrise
        
        Returns:
            str: Nom du rang (ex: "Expert")
        """
        if self.mastery_rank:
            return self.mastery_rank.rank_name
        return "Inconnu"
    
    # =========================================================================
    # MÉTHODES MÉTIER
    # =========================================================================
    
    def can_level_up(self) -> bool:
        """
        Vérifie si l'utilisateur peut monter de niveau
        
        Returns:
            bool: True si assez d'XP et pas au max
        """
        return self.experience >= self.next_level_xp and not self.is_max_level
    
    def add_experience(self, amount: int, db_session=None) -> Dict[str, Any]:
        """
        Ajoute de l'expérience et gère le level up automatique
        
        Args:
            amount: Quantité d'XP à ajouter
            db_session: Session SQLAlchemy (pour mettre à jour mastery_rank)
            
        Returns:
            Dict: Résumé des changements {leveled_up, new_level, rank_up}
        """
        result = {
            "leveled_up": False,
            "new_level": self.level,
            "rank_up": False,
            "new_rank": None,
            "xp_gained": amount
        }
        
        self.experience += amount
        
        # Level up automatique
        while self.can_level_up():
            self.level += 1
            self.experience -= self.next_level_xp
            result["leveled_up"] = True
            result["new_level"] = self.level
        
        # Vérifier promotion de rang
        if db_session and result["leveled_up"]:
            from models.mastery_rank import MasteryRank
            new_rank = MasteryRank.get_rank_for_level(db_session, self.level)
            
            if new_rank and new_rank.id != self.mastery_rank_id:
                old_rank_name = self.mastery_rank_name
                self.mastery_rank_id = new_rank.id
                result["rank_up"] = True
                result["new_rank"] = new_rank.rank_name
                result["old_rank"] = old_rank_name
        
        self.updated_at = datetime.utcnow()
        
        return result
    
    def can_craft_recipe(self, recipe) -> bool:
        """
        Vérifie si l'utilisateur peut crafter une recette
        
        Args:
            recipe: Instance de Recipe
            
        Returns:
            bool: True si niveau suffisant et même profession
        """
        if not recipe:
            return False
        
        # Vérifier profession
        if recipe.profession_id != self.profession_id:
            return False
        
        # Vérifier niveau
        if self.level < recipe.required_level:
            return False
        
        return True
    
    def calculate_craft_bonus(self) -> float:
        """
        Calcule le bonus total de crafting (mastery + autres)
        
        Returns:
            float: Multiplicateur total
        """
        return self.mastery_bonus_multiplier
    
    def get_available_subclasses(self, db_session) -> list:
        """
        Récupère les sous-classes débloquables pour ce niveau
        
        Args:
            db_session: Session SQLAlchemy
            
        Returns:
            list: Liste des sous-classes disponibles
        """
        from models.subclass import Subclass
        
        return db_session.query(Subclass).filter(
            Subclass.profession_id == self.profession_id,
            Subclass.is_active == True,
            Subclass.unlock_level <= self.level
        ).all()
    
    def time_until_max_level(self, avg_xp_per_hour: int = 500) -> float:
        """
        Estime le temps restant pour atteindre le niveau max
        
        Args:
            avg_xp_per_hour: XP moyen gagné par heure
            
        Returns:
            float: Heures estimées
        """
        if self.is_max_level or not self.profession:
            return 0.0
        
        total_xp_needed = 0
        for lvl in range(self.level, self.profession.max_level):
            total_xp_needed += lvl * 100  # Formule XP
        
        total_xp_needed -= self.experience  # Soustraire XP déjà gagnée
        
        return max(0.0, total_xp_needed / avg_xp_per_hour)
    
    # =========================================================================
    # SÉRIALISATION
    # =========================================================================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit le modèle en dictionnaire
        
        Args:
            include_relations: Inclure les relations (user, profession, mastery_rank)
            
        Returns:
            Dict: Représentation dictionnaire du modèle
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "profession_id": self.profession_id,
            "level": self.level,
            "experience": self.experience,
            "mastery_rank_id": self.mastery_rank_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # Propriétés calculées
            "next_level_xp": self.next_level_xp,
            "progress_percent": round(self.progress_percent, 2),
            "xp_remaining": self.xp_remaining,
            "is_max_level": self.is_max_level,
            "mastery_bonus_multiplier": self.mastery_bonus_multiplier,
            "mastery_rank_name": self.mastery_rank_name
        }
        
        if include_relations:
            if self.user:
                data["user"] = {
                    "id": self.user.id,
                    "login": self.user.login
                }
            
            if self.profession:
                data["profession"] = {
                    "id": self.profession.id,
                    "name": self.profession.name,
                    "type": self.profession.type,
                    "max_level": self.profession.max_level
                }
            
            if self.mastery_rank:
                data["mastery_rank"] = self.mastery_rank.to_dict()
        
        return data
    
    # =========================================================================
    # MÉTHODES MAGIQUES
    # =========================================================================
    
    def __repr__(self) -> str:
        """Représentation string du modèle"""
        return (
            f"<UserProfession(user_id={self.user_id}, profession_id={self.profession_id}, "
            f"level={self.level}, xp={self.experience}, rank={self.mastery_rank_name})>"
        )
    
    def __str__(self) -> str:
        """String lisible pour affichage"""
        profession_name = self.profession.name if self.profession else f"Profession #{self.profession_id}"
        return f"{profession_name} - Niveau {self.level} ({self.mastery_rank_name}) - {self.progress_percent:.0f}%"