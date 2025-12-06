# app/models/rarity.py

from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from datetime import datetime
from typing import Dict, Any

from database import Base


class Rarity(Base):
    """
    Modèle pour la table rarities
    
    Représente les niveaux de rareté des ressources (Commun, Rare, Épique, etc.)
    qui affectent la valeur et la drop chance.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    __tablename__ = "rarities"
    
    # =========================================================================
    # COLONNES
    # =========================================================================
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    color = Column(
        String(7), 
        nullable=False, 
        default='#FFFFFF',
        doc="Couleur hexadécimale pour l'UI (ex: #4A90E2)"
    )
    multiplier = Column(
        Numeric(5, 2), 
        nullable=False, 
        default=1.00,
        doc="Multiplicateur de valeur (1.0 = commun, 10.0 = mythique)"
    )
    drop_chance = Column(
        Numeric(5, 2), 
        nullable=False, 
        default=100.00,
        doc="Chance de drop en pourcentage (100.0 = commun, 0.1 = mythique)"
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
            'multiplier > 0',
            name='chk_rarities_multiplier'
        ),
        CheckConstraint(
            'drop_chance >= 0 AND drop_chance <= 100',
            name='chk_rarities_drop_chance'
        ),
    )
    
    # =========================================================================
    # RELATIONS
    # =========================================================================
    
    # Relation one-to-many avec resources
    resources = relationship(
        "Resource",
        back_populates="rarity",
        doc="Ressources ayant cette rareté"
    )
    
    # =========================================================================
    # PROPRIÉTÉS CALCULÉES
    # =========================================================================
    
    @property
    def is_common(self) -> bool:
        """
        Vérifie si c'est la rareté commune (multiplicateur = 1.0)
        
        Returns:
            bool: True si commun
        """
        return float(self.multiplier) == 1.0
    
    @property
    def is_rare(self) -> bool:
        """
        Vérifie si c'est une rareté rare ou supérieure (multiplicateur >= 2.0)
        
        Returns:
            bool: True si rare+
        """
        return float(self.multiplier) >= 2.0
    
    @property
    def is_very_rare(self) -> bool:
        """
        Vérifie si c'est une rareté très rare (multiplicateur >= 4.0)
        
        Returns:
            bool: True si épique+
        """
        return float(self.multiplier) >= 4.0
    
    @property
    def rarity_tier(self) -> str:
        """
        Détermine le tier de rareté
        
        Returns:
            str: "common" | "rare" | "epic" | "legendary" | "mythic"
        """
        mult = float(self.multiplier)
        if mult >= 10.0:
            return "mythic"
        elif mult >= 7.0:
            return "legendary"
        elif mult >= 4.0:
            return "epic"
        elif mult >= 2.0:
            return "rare"
        else:
            return "common"
    
    @property
    def resources_count(self) -> int:
        """
        Compte le nombre de ressources ayant cette rareté
        
        Returns:
            int: Nombre de ressources
        """
        return len(self.resources) if self.resources else 0
    
    # =========================================================================
    # MÉTHODES MÉTIER
    # =========================================================================
    
    def apply_multiplier(self, base_value: float) -> float:
        """
        Applique le multiplicateur de rareté à une valeur de base
        
        Args:
            base_value: Valeur de base de la ressource
            
        Returns:
            float: Valeur ajustée (base_value * multiplier)
        """
        return base_value * float(self.multiplier)
    
    def calculate_actual_drop_chance(self, base_chance: float = 100.0) -> float:
        """
        Calcule la chance de drop réelle
        
        Args:
            base_chance: Chance de base (100.0 = toujours)
            
        Returns:
            float: Chance réelle (base_chance * drop_chance / 100)
        """
        return (base_chance * float(self.drop_chance)) / 100.0
    
    def is_more_rare_than(self, other: 'Rarity') -> bool:
        """
        Compare la rareté avec une autre
        
        Args:
            other: Autre rareté à comparer
            
        Returns:
            bool: True si cette rareté est plus rare (multiplicateur supérieur)
        """
        return float(self.multiplier) > float(other.multiplier)
    
    @staticmethod
    def get_by_tier(db_session, tier: str) -> 'Rarity':
        """
        Récupère une rareté par son tier
        
        Args:
            db_session: Session SQLAlchemy
            tier: Tier recherché ("common", "rare", "epic", "legendary", "mythic")
            
        Returns:
            Rarity: Rareté correspondante ou None
        """
        tier_ranges = {
            "common": (0.0, 1.5),
            "rare": (1.5, 3.0),
            "epic": (3.0, 6.0),
            "legendary": (6.0, 9.0),
            "mythic": (9.0, 999.0)
        }
        
        min_mult, max_mult = tier_ranges.get(tier, (0.0, 0.0))
        
        return db_session.query(Rarity).filter(
            Rarity.multiplier >= min_mult,
            Rarity.multiplier < max_mult
        ).first()
    
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
            "color": self.color,
            "multiplier": float(self.multiplier),
            "drop_chance": float(self.drop_chance),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Propriétés calculées
            "is_common": self.is_common,
            "is_rare": self.is_rare,
            "is_very_rare": self.is_very_rare,
            "rarity_tier": self.rarity_tier,
            "resources_count": self.resources_count
        }
        
        if include_relations and self.resources:
            data["resources"] = [
                {"id": r.id, "name": r.name, "base_value": float(r.base_value)} 
                for r in self.resources
            ]
        
        return data
    
    # =========================================================================
    # MÉTHODES MAGIQUES
    # =========================================================================
    
    def __repr__(self) -> str:
        """Représentation string du modèle"""
        return (
            f"<Rarity(id={self.id}, name='{self.name}', "
            f"multiplier={self.multiplier}, drop={self.drop_chance}%)>"
        )
    
    def __str__(self) -> str:
        """String lisible pour affichage"""
        return f"{self.name} (×{self.multiplier}, {self.drop_chance}% drop)"
    
    def __lt__(self, other: 'Rarity') -> bool:
        """Comparaison < pour tri par rareté"""
        return float(self.multiplier) < float(other.multiplier)
    
    def __le__(self, other: 'Rarity') -> bool:
        """Comparaison <= pour tri"""
        return float(self.multiplier) <= float(other.multiplier)
    
    def __gt__(self, other: 'Rarity') -> bool:
        """Comparaison > pour tri"""
        return float(self.multiplier) > float(other.multiplier)
    
    def __ge__(self, other: 'Rarity') -> bool:
        """Comparaison >= pour tri"""
        return float(self.multiplier) >= float(other.multiplier)