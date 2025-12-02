# app/database/models.py
"""
Modèles SQLAlchemy pour PostgreSQL.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, Float, DateTime, Index, Text
from sqlalchemy.sql import func
from datetime import datetime
from database.connection import Base


# ============================================================================
# USER
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    # Colonnes
    id = Column(String(36), primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    mail = Column(String(255), unique=True, nullable=False, index=True)
    login = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Game data
    profession = Column(String(50), default="", index=True)
    subclasses = Column(JSON, default=list)  # Liste de strings
    inventory = Column(JSON, default=dict)   # {item_id: quantity}
    
    # Progression
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1, index=True)
    stats = Column(JSON, default=lambda: {"strength": 1, "agility": 1, "endurance": 1})
    
    # Gameplay
    biome = Column(String(50), default="")
    
    # Roles
    is_admin = Column(Boolean, default=False, index=True)
    is_moderator = Column(Boolean, default=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Index composites pour performances
    __table_args__ = (
        Index('ix_users_profession_level', 'profession', 'level'),
    )
    
    def to_dict(self):
        """Conversion en dict pour compatibilité avec ancien code."""
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


# ============================================================================
# REFRESH TOKEN
# ============================================================================

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    token_hash = Column(String(64), primary_key=True)  # Hash HMAC du token
    user_id = Column(String(36), nullable=False, index=True)
    device_id = Column(String(100), nullable=False)
    device_name = Column(String(255), default="")
    
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Index composite pour nettoyage des tokens expirés
    __table_args__ = (
        Index('ix_refresh_tokens_user_device', 'user_id', 'device_id'),
    )


# ============================================================================
# PROFESSION
# ============================================================================

class Profession(Base):
    __tablename__ = "professions"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    
    resources_found = Column(JSON, default=list)  # Liste d'IDs de ressources
    allowed_recipes = Column(JSON, default=list)  # Liste d'IDs de recettes
    subclasses = Column(JSON, default=list)       # Liste de sous-classes
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resources_found": self.resources_found or [],
            "allowed_recipes": self.allowed_recipes or [],
            "subclasses": self.subclasses or [],
        }


# ============================================================================
# RESOURCE
# ============================================================================

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    description = Column(Text, default="")
    
    # Optionnel: propriétés physiques
    weight = Column(Float, default=1.0)
    stack_size = Column(Integer, default=999)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "weight": self.weight,
            "stack_size": self.stack_size,
        }


# ============================================================================
# RECIPE
# ============================================================================

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(String(50), primary_key=True)
    output = Column(String(50), nullable=False)  # ID de la ressource produite
    ingredients = Column(JSON, nullable=False)   # {resource_id: quantity}
    required_profession = Column(String(50), nullable=False, index=True)
    
    # Optionnel: prérequis de niveau
    required_level = Column(Integer, default=1)
    xp_reward = Column(Integer, default=10)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "output": self.output,
            "ingredients": self.ingredients or {},
            "required_profession": self.required_profession,
            "required_level": self.required_level,
            "xp_reward": self.xp_reward,
        }


# ============================================================================
# LOOT TABLE
# ============================================================================

class LootTable(Base):
    __tablename__ = "loot_tables"
    
    id = Column(String(50), primary_key=True)
    biomes = Column(JSON, default=list)  # Liste de biomes applicables
    entries = Column(JSON, nullable=False)  # Liste d'entrées de loot
    
    # Format entries:
    # [
    #   {"item": "argile", "weight": 40, "min": 1, "max": 3, "rarity": "common"},
    #   ...
    # ]
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "biomes": self.biomes or [],
            "table": self.entries or [],
        }


# ============================================================================
# QUEST
# ============================================================================

class Quest(Base):
    __tablename__ = "quests"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    
    requirements = Column(JSON, default=dict)  # {"collect": {"wood": 10}}
    rewards = Column(JSON, default=dict)       # {"xp": 100, "items": {"coin": 5}}
    
    # Conditions
    required_level = Column(Integer, default=1)
    required_profession = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
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


# ============================================================================
# SETTINGS (pour feature flags)
# ============================================================================

class Setting(Base):
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)  # Peut stocker bool, int, string, dict...
    description = Column(Text, default="")
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ============================================================================
# FAILED LOGIN (brute force protection)
# ============================================================================

class FailedLogin(Base):
    __tablename__ = "failed_logins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv6 support
    attempted_at = Column(DateTime, server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('ix_failed_logins_login_time', 'login', 'attempted_at'),
    )