# app/models/profession.py
"""
Modèle SQLAlchemy pour les professions.
"""

from sqlalchemy import Column, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from database.connection import Base


class Profession(Base):
    __tablename__ = "professions"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    
    resources_found = Column(JSON, default=list, nullable=False)
    allowed_recipes = Column(JSON, default=list, nullable=False)
    subclasses = Column(JSON, default=list, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resources_found": self.resources_found or [],
            "allowed_recipes": self.allowed_recipes or [],
            "subclasses": self.subclasses or [],
        }