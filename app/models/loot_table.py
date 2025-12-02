# app/database/models/lootTable.py
"""
Modèles SQLAlchemy pour LootTable
"""

from sqlalchemy import Column, String, JSON, Integer, DateTime, Text
from sqlalchemy.sql import func
from database.connection import Base


class LootTable(Base):
    __tablename__ = "loot_tables"
    
    id = Column(String(50), primary_key=True)
    biomes = Column(JSON, default=list, nullable=False)
    entries = Column(JSON, nullable=False)  # Format: [{"item": "...", "weight": ..., "min": ..., "max": ..., "rarity": "..."}]
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "biomes": self.biomes or [],
            "table": self.entries or [],
        }