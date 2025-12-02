# app/models/resource.py
"""
Modèle SQLAlchemy pour les ressources.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Index
from sqlalchemy.sql import func
from database.connection import Base


class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    description = Column(Text, default="")
    
    # Propriétés physiques
    weight = Column(Float, default=1.0, nullable=False)
    stack_size = Column(Integer, default=999, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "weight": self.weight,
            "stack_size": self.stack_size,
        }