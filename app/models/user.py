# app/models/user.py
"""
Modèle SQLAlchemy pour les utilisateurs.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, Index
from sqlalchemy.sql import func
from database.connection import Base


class User(Base):
    __tablename__ = "users"
    
    # Identification
    id = Column(String(36), primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    mail = Column(String(255), unique=True, nullable=False, index=True)
    login = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Game data
    profession = Column(String(50), default="", index=True)
    subclasses = Column(JSON, default=list, nullable=False)
    inventory = Column(JSON, default=dict, nullable=False)
    
    # Progression
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False, index=True)
    stats = Column(JSON, default=lambda: {"strength": 1, "agility": 1, "endurance": 1}, nullable=False)
    
    # Gameplay
    biome = Column(String(50), default="")
    
    # Roles
    is_admin = Column(Boolean, default=False, nullable=False, index=True)
    is_moderator = Column(Boolean, default=False, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Index composites
    __table_args__ = (
        Index('ix_users_profession_level', 'profession', 'level'),
    )
    
    def to_dict(self):
        """Conversion en dict pour compatibilité."""
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "mail": self.mail,
            "login": self.login,
            "password_hash": self.password_hash,
            "profession": self.profession,
            "subclasses": self.subclasses or [],
            "inventory": self.inventory or {},
            "xp": self.xp,
            "level": self.level,
            "stats": self.stats or {"strength": 1, "agility": 1, "endurance": 1},
            "biome": self.biome,
            "is_admin": self.is_admin,
            "is_moderator": self.is_moderator,
        }