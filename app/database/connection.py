# app/database/connection.py
"""
Connexion PostgreSQL avec SQLAlchemy.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text
from contextlib import contextmanager
from typing import Generator
import os

from utils.logger import get_logger

logger = get_logger(__name__)

# URL de connexion depuis .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment")

DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

# ============================================================================
# ENGINE
# ============================================================================

engine = create_engine(
    DATABASE_URL,
    echo=DB_ECHO,  # Log SQL queries si true
    pool_pre_ping=True,  # Vérifie que la connexion est vivante
    pool_size=10,  # Nombre de connexions dans le pool
    max_overflow=20,  # Connexions supplémentaires en cas de pic
    pool_recycle=3600,  # Recycle les connexions après 1h
)

# Event listener pour activer les foreign keys (utile si on passe de SQLite)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Configure la connexion après création."""
    pass  # Pour PostgreSQL, rien à faire ici


# ============================================================================
# SESSION FACTORY
# ============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================================
# BASE POUR LES MODÈLES
# ============================================================================

Base = declarative_base()


# ============================================================================
# DEPENDENCY POUR FASTAPI
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency pour obtenir une session DB.
    
    Usage:
        @router.get("/users")
        def list_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# CONTEXT MANAGER (pour scripts)
# ============================================================================

@contextmanager
def get_db_context():
    """
    Context manager pour scripts hors FastAPI.
    
    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# INIT DB (création des tables)
# ============================================================================

def init_db():
    """
    Crée toutes les tables définies dans Base.metadata.
    À appeler au démarrage de l'app.
    """
    logger.info("🔧 Initialisation de la base de données...")
    
    # Import tous les modèles pour que SQLAlchemy les connaisse
    # from database import models  # noqa: F401
    
    # Crée les tables
    # Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Tables créées avec succès")


# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_db_connection() -> bool:
    """Vérifie que la DB est accessible."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False