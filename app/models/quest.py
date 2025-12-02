# app/database/models/quest.py
"""
Modèles SQLAlchemy pour Quest.
"""

from sqlalchemy import Column, String, JSON, Integer, DateTime, Text
from sqlalchemy.sql import func
from database.connection import Base


class Quest(Base):
    __tablename__ = "quests"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    
    requirements = Column(JSON, default=dict, nullable=False)  # {"collect": {"wood": 10}}
    rewards = Column(JSON, default=dict, nullable=False)       # {"xp": 100, "items": {"coin": 5}}
    
    # Conditions
    required_level = Column(Integer, default=1, nullable=False)
    required_profession = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "requirements": self.requirements or {},
            "reward": self.rewards or {},
            "required_level": self.required_level,
            "required_profession": self.required_profession,
        }