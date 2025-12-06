"""
Module: models.user_statistics
Version: 3.0
"""

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from database import Base


class UserStatistics(Base):
    """
    Modèle pour la table user_statistics
    
    Stocke les statistiques temps réel d'un joueur.
    Mis à jour automatiquement par triggers SQL lors d'actions du joueur.
    
    Attributes:
        id (int): Identifiant unique
        user_id (int): Référence à l'utilisateur
        total_crafts (int): Nombre total d'objets craftés
        total_sales (int): Nombre total de ventes sur le marché
        total_purchases (int): Nombre total d'achats sur le marché
        total_resources_gathered (int): Nombre total de ressources récoltées
        total_gold_earned (int): Or total gagné (ventes)
        total_gold_spent (int): Or total dépensé (achats)
        workshops_built (int): Nombre d'ateliers construits
        workshops_repaired (int): Nombre de réparations d'ateliers
        rare_items_crafted (int): Nombre d'objets rares/légendaires craftés
        professions_mastered (int): Nombre de professions au rang Maître
        achievements_unlocked (int): Nombre de succès débloqués
        play_time_minutes (int): Temps de jeu total en minutes
        last_craft_at (datetime): Date du dernier craft
        last_sale_at (datetime): Date de la dernière vente
        last_purchase_at (datetime): Date du dernier achat
        created_at (datetime): Date de création
        updated_at (datetime): Date de dernière mise à jour
    
    Relations:
        user: Utilisateur associé
    
    Notes:
        - Table 1-to-1 avec users (1 user = 1 statistics)
        - Mise à jour automatique par triggers SQL
        - Utilisé pour leaderboards, profils, achievements
    """
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "user_statistics"
    
    # Colonnes principales
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Statistiques de crafting
    total_crafts = Column(BigInteger, nullable=False, default=0)
    total_resources_gathered = Column(BigInteger, nullable=False, default=0)
    rare_items_crafted = Column(Integer, nullable=False, default=0)
    
    # Statistiques de marché
    total_sales = Column(Integer, nullable=False, default=0)
    total_purchases = Column(Integer, nullable=False, default=0)
    total_gold_earned = Column(BigInteger, nullable=False, default=0)
    total_gold_spent = Column(BigInteger, nullable=False, default=0)
    
    # Statistiques d'ateliers
    workshops_built = Column(Integer, nullable=False, default=0)
    workshops_repaired = Column(Integer, nullable=False, default=0)
    
    # Statistiques de progression
    professions_mastered = Column(Integer, nullable=False, default=0)
    achievements_unlocked = Column(Integer, nullable=False, default=0)
    
    # Temps de jeu
    play_time_minutes = Column(BigInteger, nullable=False, default=0)
    
    # Dernières activités
    last_craft_at = Column(TIMESTAMP(timezone=True), nullable=True, index=True)
    last_sale_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_purchase_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Timestamps
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
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('total_crafts >= 0', name='check_total_crafts_positive'),
        CheckConstraint('total_sales >= 0', name='check_total_sales_positive'),
        CheckConstraint('total_purchases >= 0', name='check_total_purchases_positive'),
        CheckConstraint('total_resources_gathered >= 0', name='check_total_gathered_positive'),
        CheckConstraint('total_gold_earned >= 0', name='check_total_earned_positive'),
        CheckConstraint('total_gold_spent >= 0', name='check_total_spent_positive'),
        CheckConstraint('workshops_built >= 0', name='check_workshops_built_positive'),
        CheckConstraint('workshops_repaired >= 0', name='check_workshops_repaired_positive'),
        CheckConstraint('rare_items_crafted >= 0', name='check_rare_items_positive'),
        CheckConstraint('professions_mastered >= 0', name='check_professions_mastered_positive'),
        CheckConstraint('achievements_unlocked >= 0', name='check_achievements_positive'),
        CheckConstraint('play_time_minutes >= 0', name='check_play_time_positive'),
    )
    
    # Relations
    user = relationship(
        "User",
        back_populates="statistics",
        lazy="joined",
        uselist=False
    )
    
    # ==================== PROPRIÉTÉS CALCULÉES ====================
    
    @property
    def net_gold(self) -> int:
        """
        Calcule le bilan d'or (gagné - dépensé)
        
        Returns:
            int: Or net (peut être négatif)
        """
        return self.total_gold_earned - self.total_gold_spent
    
    @property
    def craft_rate(self) -> float:
        """
        Calcule le taux de craft par heure de jeu
        
        Returns:
            float: Crafts/heure (0.0 si pas de temps de jeu)
        """
        if self.play_time_minutes == 0:
            return 0.0
        
        hours = self.play_time_minutes / 60.0
        return round(self.total_crafts / hours, 2)
    
    @property
    def gold_per_hour(self) -> float:
        """
        Calcule l'or gagné par heure de jeu
        
        Returns:
            float: Or/heure (0.0 si pas de temps de jeu)
        """
        if self.play_time_minutes == 0:
            return 0.0
        
        hours = self.play_time_minutes / 60.0
        return round(self.total_gold_earned / hours, 2)
    
    @property
    def average_sale_price(self) -> float:
        """
        Calcule le prix moyen d'une vente
        
        Returns:
            float: Prix moyen (0.0 si pas de ventes)
        """
        if self.total_sales == 0:
            return 0.0
        
        return round(self.total_gold_earned / self.total_sales, 2)
    
    @property
    def average_purchase_price(self) -> float:
        """
        Calcule le prix moyen d'un achat
        
        Returns:
            float: Prix moyen (0.0 si pas d'achats)
        """
        if self.total_purchases == 0:
            return 0.0
        
        return round(self.total_gold_spent / self.total_purchases, 2)
    
    @property
    def play_time_hours(self) -> float:
        """
        Convertit le temps de jeu en heures
        
        Returns:
            float: Temps de jeu en heures
        """
        return round(self.play_time_minutes / 60.0, 2)
    
    @property
    def play_time_formatted(self) -> str:
        """
        Formate le temps de jeu en texte lisible
        
        Returns:
            str: "5j 12h 30m" ou "2h 15m"
        """
        total_minutes = self.play_time_minutes
        
        days = total_minutes // (24 * 60)
        hours = (total_minutes % (24 * 60)) // 60
        minutes = total_minutes % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}j")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or not parts:
            parts.append(f"{minutes}m")
        
        return " ".join(parts)
    
    @property
    def is_active_player(self) -> bool:
        """
        Vérifie si le joueur est actif (activité dans les 7 derniers jours)
        
        Returns:
            bool: True si actif récemment
        """
        if not self.last_craft_at:
            return False
        
        seven_days_ago = datetime.now(self.last_craft_at.tzinfo) - timedelta(days=7)
        return self.last_craft_at > seven_days_ago
    
    @property
    def days_since_last_craft(self) -> Optional[int]:
        """
        Calcule le nombre de jours depuis le dernier craft
        
        Returns:
            int: Nombre de jours ou None si jamais crafté
        """
        if not self.last_craft_at:
            return None
        
        delta = datetime.now(self.last_craft_at.tzinfo) - self.last_craft_at
        return delta.days
    
    @property
    def rare_items_percentage(self) -> float:
        """
        Calcule le pourcentage d'items rares craftés
        
        Returns:
            float: Pourcentage (0.0-100.0)
        """
        if self.total_crafts == 0:
            return 0.0
        
        return round((self.rare_items_crafted / self.total_crafts) * 100, 2)
    
    # ==================== MÉTHODES D'INCRÉMENTATION ====================
    
    def increment_craft(self, is_rare: bool = False) -> None:
        """
        Incrémente le nombre de crafts
        
        Args:
            is_rare (bool): Si True, incrémente aussi rare_items_crafted
        """
        self.total_crafts += 1
        if is_rare:
            self.rare_items_crafted += 1
        self.last_craft_at = func.now()
        self.updated_at = func.now()
    
    def increment_sale(self, amount: float) -> None:
        """
        Incrémente les statistiques de vente
        
        Args:
            amount (float): Montant de la vente
        """
        self.total_sales += 1
        self.total_gold_earned += int(amount * 100)  # Convertir en centièmes
        self.last_sale_at = func.now()
        self.updated_at = func.now()
    
    def increment_purchase(self, amount: float) -> None:
        """
        Incrémente les statistiques d'achat
        
        Args:
            amount (float): Montant de l'achat
        """
        self.total_purchases += 1
        self.total_gold_spent += int(amount * 100)  # Convertir en centièmes
        self.last_purchase_at = func.now()
        self.updated_at = func.now()
    
    def increment_gather(self, amount: int = 1) -> None:
        """
        Incrémente le nombre de ressources récoltées
        
        Args:
            amount (int): Nombre de ressources récoltées
        """
        self.total_resources_gathered += amount
        self.updated_at = func.now()
    
    def increment_workshop_built(self) -> None:
        """Incrémente le nombre d'ateliers construits"""
        self.workshops_built += 1
        self.updated_at = func.now()
    
    def increment_workshop_repaired(self) -> None:
        """Incrémente le nombre de réparations d'ateliers"""
        self.workshops_repaired += 1
        self.updated_at = func.now()
    
    def increment_profession_mastered(self) -> None:
        """Incrémente le nombre de professions maîtrisées"""
        self.professions_mastered += 1
        self.updated_at = func.now()
    
    def increment_achievement(self) -> None:
        """Incrémente le nombre de succès débloqués"""
        self.achievements_unlocked += 1
        self.updated_at = func.now()
    
    def add_play_time(self, minutes: int) -> None:
        """
        Ajoute du temps de jeu
        
        Args:
            minutes (int): Minutes de jeu à ajouter
        """
        if minutes > 0:
            self.play_time_minutes += minutes
            self.updated_at = func.now()
    
    # ==================== MÉTHODES DE COMPARAISON ====================
    
    def compare_with(self, other: 'UserStatistics') -> Dict[str, Any]:
        """
        Compare ces statistiques avec celles d'un autre joueur
        
        Args:
            other (UserStatistics): Statistiques de l'autre joueur
        
        Returns:
            dict: Différences (positif = meilleur, négatif = moins bon)
        """
        return {
            "total_crafts_diff": self.total_crafts - other.total_crafts,
            "total_sales_diff": self.total_sales - other.total_sales,
            "net_gold_diff": self.net_gold - other.net_gold,
            "craft_rate_diff": self.craft_rate - other.craft_rate,
            "gold_per_hour_diff": self.gold_per_hour - other.gold_per_hour,
            "play_time_diff": self.play_time_minutes - other.play_time_minutes,
            "professions_mastered_diff": self.professions_mastered - other.professions_mastered
        }
    
    def get_rank_score(self) -> float:
        """
        Calcule un score global pour le classement
        
        Formule: (crafts * 1) + (sales * 2) + (gold_earned * 0.001) + 
                 (professions_mastered * 100) + (achievements * 50)
        
        Returns:
            float: Score total
        """
        score = (
            self.total_crafts * 1.0 +
            self.total_sales * 2.0 +
            self.total_gold_earned * 0.001 +
            self.professions_mastered * 100.0 +
            self.achievements_unlocked * 50.0 +
            self.rare_items_crafted * 5.0
        )
        return round(score, 2)
    
    # ==================== MÉTHODES STATIQUES ====================
    
    @staticmethod
    def get_top_crafters(session, limit: int = 10):
        """
        Récupère les meilleurs crafteurs
        
        Args:
            session: Session SQLAlchemy
            limit (int): Nombre de résultats
        
        Returns:
            list[UserStatistics]: Top crafteurs
        """
        return session.query(UserStatistics)\
            .order_by(UserStatistics.total_crafts.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_top_traders(session, limit: int = 10):
        """
        Récupère les meilleurs traders
        
        Args:
            session: Session SQLAlchemy
            limit (int): Nombre de résultats
        
        Returns:
            list[UserStatistics]: Top traders
        """
        return session.query(UserStatistics)\
            .order_by(UserStatistics.total_sales.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_richest_players(session, limit: int = 10):
        """
        Récupère les joueurs les plus riches (par or gagné)
        
        Args:
            session: Session SQLAlchemy
            limit (int): Nombre de résultats
        
        Returns:
            list[UserStatistics]: Joueurs les plus riches
        """
        return session.query(UserStatistics)\
            .order_by(UserStatistics.total_gold_earned.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_leaderboard(session, limit: int = 100):
        """
        Récupère le classement global (par rank_score)
        
        Args:
            session: Session SQLAlchemy
            limit (int): Nombre de résultats
        
        Returns:
            list[tuple]: Liste de (UserStatistics, rank_score)
        """
        stats = session.query(UserStatistics).all()
        
        # Calculer les scores et trier
        leaderboard = [(stat, stat.get_rank_score()) for stat in stats]
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        
        return leaderboard[:limit]
    
    # ==================== SÉRIALISATION ====================
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Convertit les statistiques en dictionnaire
        
        Args:
            include_relations (bool): Inclure les détails de l'utilisateur
        
        Returns:
            dict: Représentation JSON des statistiques
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            
            # Statistiques brutes
            "total_crafts": self.total_crafts,
            "total_sales": self.total_sales,
            "total_purchases": self.total_purchases,
            "total_resources_gathered": self.total_resources_gathered,
            "total_gold_earned": self.total_gold_earned / 100.0,  # Convertir en float
            "total_gold_spent": self.total_gold_spent / 100.0,
            "workshops_built": self.workshops_built,
            "workshops_repaired": self.workshops_repaired,
            "rare_items_crafted": self.rare_items_crafted,
            "professions_mastered": self.professions_mastered,
            "achievements_unlocked": self.achievements_unlocked,
            "play_time_minutes": self.play_time_minutes,
            
            # Statistiques calculées
            "net_gold": self.net_gold / 100.0,
            "craft_rate": self.craft_rate,
            "gold_per_hour": self.gold_per_hour,
            "average_sale_price": self.average_sale_price,
            "average_purchase_price": self.average_purchase_price,
            "play_time_hours": self.play_time_hours,
            "play_time_formatted": self.play_time_formatted,
            "is_active_player": self.is_active_player,
            "days_since_last_craft": self.days_since_last_craft,
            "rare_items_percentage": self.rare_items_percentage,
            "rank_score": self.get_rank_score(),
            
            # Dates
            "last_craft_at": self.last_craft_at.isoformat() if self.last_craft_at else None,
            "last_sale_at": self.last_sale_at.isoformat() if self.last_sale_at else None,
            "last_purchase_at": self.last_purchase_at.isoformat() if self.last_purchase_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_relations and self.user:
            data["user"] = {
                "id": self.user.id,
                "login": self.user.login,
                "gold": self.user.gold
            }
        
        return data
    
    def __repr__(self) -> str:
        """Représentation string des statistiques"""
        return (
            f"<UserStatistics(user_id={self.user_id}, "
            f"crafts={self.total_crafts}, "
            f"sales={self.total_sales}, "
            f"gold={self.net_gold / 100.0:.2f})>"
        )