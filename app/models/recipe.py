# app/models/recipe.py
"""
Modèle SQLAlchemy pour les recettes de crafting.
"""

from sqlalchemy import Column, String, JSON, Integer, DateTime, Index
from sqlalchemy.sql import func
from database.connection import Base


class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(String(50), primary_key=True)
    output = Column(String(50), nullable=False)
    ingredients = Column(JSON, nullable=False)
    required_profession = Column(String(50), nullable=False, index=True)
    
    # Prérequis et récompenses
    required_level = Column(Integer, default=1, nullable=False)
    xp_reward = Column(Integer, default=10, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "output": self.output,
            "ingredients": self.ingredients or {},
            "required_profession": self.required_profession,
            "required_level": self.required_level,
            "xp_reward": self.xp_reward,
        }