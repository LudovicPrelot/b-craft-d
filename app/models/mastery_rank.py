# app/models/mastery_rank


from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from datetime import datetime
from typing import Dict, Any, Optional, List

from database import Base


class MasteryRank(Base):
    """
    Modèle pour la table mastery_rank
    
    Représente les rangs de maîtrise d'une profession
    (Débutant, Apprenti, Compagnon, Expert, Maître)
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    __tablename__ = "mastery_rank"
    
    # Constantes de classe pour les rangs
    RANK_DEBUTANT = "Débutant"
    RANK_APPRENTI = "Apprenti"
    RANK_COMPAGNON = "Compagnon"
    RANK_EXPERT = "Expert"
    RANK_MAITRE = "Maître"
    
    # =========================================================================
    # COLONNES
    # =========================================================================
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rank_name = Column(
        String(50), 
        nullable=False, 
        unique=True, 
        index=True,
        doc="Nom du rang de maîtrise"
    )
    min_level = Column(
        Integer, 
        nullable=False,
        index=True,
        doc="Niveau minimum pour ce rang"
    )
    bonus_multiplier = Column(
        Numeric(5, 2), 
        nullable=False, 
        default=1.00,
        doc="Multiplicateur de bonus (1.0 = 0%, 1.5 = +50%)"
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
            'min_level >= 1',
            name='chk_mastery_rank_min_level'
        ),
        CheckConstraint(
            'bonus_multiplier >= 1.00',
            name='chk_mastery_rank_bonus_multiplier'
        ),
    )
    
    # =========================================================================
    # RELATIONS
    # =========================================================================
    
    # Relation one-to-many avec users_professions
    user_professions = relationship(
        "UserProfession",
        back_populates="mastery_rank",
        doc="Utilisateurs ayant ce rang de maîtrise"
    )
    
    # =========================================================================
    # PROPRIÉTÉS CALCULÉES
    # =========================================================================
    
    @property
    def bonus_percent(self) -> float:
        """
        Convertit le multiplicateur en pourcentage de bonus
        
        Returns:
            float: Bonus en pourcentage (ex: 50.0 pour +50%)
        """
        return (float(self.bonus_multiplier) - 1.0) * 100
    
    @property
    def is_beginner(self) -> bool:
        """Vérifie si c'est le rang débutant"""
        return self.rank_name == self.RANK_DEBUTANT or self.min_level == 1
    
    @property
    def is_master(self) -> bool:
        """Vérifie si c'est le rang maître (plus haut)"""
        return self.rank_name == self.RANK_MAITRE or float(self.bonus_multiplier) >= 2.0
    
    @property
    def users_count(self) -> int:
        """
        Compte le nombre d'utilisateurs ayant ce rang
        
        Returns:
            int: Nombre d'utilisateurs
        """
        return len(self.user_professions) if self.user_professions else 0
    
    @property
    def rank_tier(self) -> int:
        """
        Détermine le tier du rang (1-5)
        
        Returns:
            int: Tier (1 = Débutant, 5 = Maître)
        """
        rank_tiers = {
            self.RANK_DEBUTANT: 1,
            self.RANK_APPRENTI: 2,
            self.RANK_COMPAGNON: 3,
            self.RANK_EXPERT: 4,
            self.RANK_MAITRE: 5
        }
        return rank_tiers.get(self.rank_name, 1)
    
    # =========================================================================
    # MÉTHODES MÉTIER
    # =========================================================================
    
    def can_promote_from_level(self, current_level: int) -> bool:
        """
        Vérifie si un niveau permet d'atteindre ce rang
        
        Args:
            current_level: Niveau actuel de la profession
            
        Returns:
            bool: True si le niveau est suffisant
        """
        return current_level >= self.min_level
    
    def apply_bonus(self, base_value: float) -> float:
        """
        Applique le multiplicateur de maîtrise à une valeur de base
        
        Args:
            base_value: Valeur de base
            
        Returns:
            float: Valeur avec bonus de maîtrise
        """
        return base_value * float(self.bonus_multiplier)
    
    def get_next_rank(self, db_session) -> Optional['MasteryRank']:
        """
        Récupère le rang suivant dans la hiérarchie
        
        Args:
            db_session: Session SQLAlchemy
            
        Returns:
            MasteryRank: Rang suivant ou None si déjà au maximum
        """
        if self.is_master:
            return None
        
        return db_session.query(MasteryRank).filter(
            MasteryRank.min_level > self.min_level
        ).order_by(MasteryRank.min_level.asc()).first()
    
    def get_previous_rank(self, db_session) -> Optional['MasteryRank']:
        """
        Récupère le rang précédent dans la hiérarchie
        
        Args:
            db_session: Session SQLAlchemy
            
        Returns:
            MasteryRank: Rang précédent ou None si déjà au minimum
        """
        if self.is_beginner:
            return None
        
        return db_session.query(MasteryRank).filter(
            MasteryRank.min_level < self.min_level
        ).order_by(MasteryRank.min_level.desc()).first()
    
    @staticmethod
    def get_rank_for_level(db_session, level: int) -> Optional['MasteryRank']:
        """
        Récupère le rang de maîtrise correspondant à un niveau
        
        Args:
            db_session: Session SQLAlchemy
            level: Niveau de la profession
            
        Returns:
            MasteryRank: Rang correspondant ou None
        """
        return db_session.query(MasteryRank).filter(
            MasteryRank.min_level <= level
        ).order_by(MasteryRank.min_level.desc()).first()
    
    @staticmethod
    def get_all_ranks_ordered(db_session) -> List['MasteryRank']:
        """
        Récupère tous les rangs triés par niveau croissant
        
        Args:
            db_session: Session SQLAlchemy
            
        Returns:
            List[MasteryRank]: Liste ordonnée des rangs
        """
        return db_session.query(MasteryRank).order_by(MasteryRank.min_level.asc()).all()
    
    @staticmethod
    def get_rank_by_name(db_session, rank_name: str) -> Optional['MasteryRank']:
        """
        Récupère un rang par son nom
        
        Args:
            db_session: Session SQLAlchemy
            rank_name: Nom du rang
            
        Returns:
            MasteryRank: Rang trouvé ou None
        """
        return db_session.query(MasteryRank).filter(
            MasteryRank.rank_name == rank_name
        ).first()
    
    def levels_until_next_rank(self, current_level: int, db_session) -> Optional[int]:
        """
        Calcule combien de niveaux restent avant le rang suivant
        
        Args:
            current_level: Niveau actuel
            db_session: Session SQLAlchemy
            
        Returns:
            int: Niveaux manquants ou None si déjà au maximum
        """
        next_rank = self.get_next_rank(db_session)
        if not next_rank:
            return None
        
        return max(0, next_rank.min_level - current_level)
    
    # =========================================================================
    # SÉRIALISATION
    # =========================================================================
    
    def to_dict(self, include_relations: bool = False, db_session=None) -> Dict[str, Any]:
        """
        Convertit le modèle en dictionnaire
        
        Args:
            include_relations: Inclure les relations (users)
            db_session: Session pour récupérer next/previous ranks
            
        Returns:
            Dict: Représentation dictionnaire du modèle
        """
        data = {
            "id": self.id,
            "rank_name": self.rank_name,
            "min_level": self.min_level,
            "bonus_multiplier": float(self.bonus_multiplier),
            "bonus_percent": self.bonus_percent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Propriétés calculées
            "is_beginner": self.is_beginner,
            "is_master": self.is_master,
            "users_count": self.users_count,
            "rank_tier": self.rank_tier
        }
        
        if db_session:
            next_rank = self.get_next_rank(db_session)
            prev_rank = self.get_previous_rank(db_session)
            
            data["next_rank"] = {
                "id": next_rank.id,
                "name": next_rank.rank_name,
                "min_level": next_rank.min_level
            } if next_rank else None
            
            data["previous_rank"] = {
                "id": prev_rank.id,
                "name": prev_rank.rank_name,
                "min_level": prev_rank.min_level
            } if prev_rank else None
        
        if include_relations and self.user_professions:
            data["users"] = [
                {
                    "user_id": up.user_id,
                    "profession_id": up.profession_id,
                    "level": up.level
                } 
                for up in self.user_professions[:10]  # Limiter à 10
            ]
        
        return data
    
    # =========================================================================
    # MÉTHODES MAGIQUES
    # =========================================================================
    
    def __repr__(self) -> str:
        """Représentation string du modèle"""
        return (
            f"<MasteryRank(id={self.id}, rank='{self.rank_name}', "
            f"min_level={self.min_level}, multiplier={self.bonus_multiplier})>"
        )
    
    def __str__(self) -> str:
        """String lisible pour affichage"""
        return f"{self.rank_name} (Niveau {self.min_level}+) - Bonus ×{self.bonus_multiplier}"
    
    def __lt__(self, other: 'MasteryRank') -> bool:
        """Comparaison < pour tri par niveau minimum"""
        return self.min_level < other.min_level
    
    def __le__(self, other: 'MasteryRank') -> bool:
        """Comparaison <="""
        return self.min_level <= other.min_level
    
    def __gt__(self, other: 'MasteryRank') -> bool:
        """Comparaison >"""
        return self.min_level > other.min_level
    
    def __ge__(self, other: 'MasteryRank') -> bool:
        """Comparaison >="""
        return self.min_level >= other.min_level