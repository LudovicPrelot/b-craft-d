# app/routes/api/user/professions.py
"""
Routes user pour les professions (lecture + filtrage par user).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from utils.roles import require_user
from utils.logger import get_logger
from utils.db_crud import profession_crud
from database.connection import get_db
from schemas.profession import ProfessionResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Users - Professions"], dependencies=[Depends(require_user)])


@router.get("/", response_model=List[ProfessionResponse])
def list_professions(
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Liste toutes les professions.
    
    Authentification requise.
    """
    user_id = current.get("id")
    logger.info(f"📋 User {user_id}: Liste des professions")
    
    professions = profession_crud.get_multi(db, limit=100)
    
    logger.debug(f"   → {len(professions)} profession(s)")
    return professions


@router.get("/{profession_id}", response_model=ProfessionResponse)
def get_profession(
    profession_id: str,
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """Récupère une profession."""
    user_id = current.get("id")
    logger.info(f"🔍 User {user_id}: Récupération profession '{profession_id}'")
    
    profession = profession_crud.get_or_404(db, profession_id, "Profession")
    
    return profession