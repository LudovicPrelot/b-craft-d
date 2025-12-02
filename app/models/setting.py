# app/database/models/setting.py
"""
Modèles SQLAlchemy pour Setting.
"""

from sqlalchemy import Column, String, JSON, Integer, DateTime, Text
from sqlalchemy.sql import func
from database.connection import Base


class Setting(Base):
    """Modèle pour les paramètres de l'application (feature flags)."""
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, default="")
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)