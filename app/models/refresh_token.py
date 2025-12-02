# app/models/refresh_token.py
"""
Modèle SQLAlchemy pour les refresh tokens.
"""

from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
from database.connection import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    token_hash = Column(String(64), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    device_id = Column(String(100), nullable=False)
    device_name = Column(String(255), default="")
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    __table_args__ = (
        Index('ix_refresh_tokens_user_device', 'user_id', 'device_id'),
    )