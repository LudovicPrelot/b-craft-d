# app/routes/api/public/professions.py
"""
Routes publiques pour les professions (lecture seule).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from utils.logger import get_logger
from utils.db_crud import profession_crud
from database.connection import get_db
from schemas.profession import ProfessionResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Public - Professions"])


@router.get("/", response_model=List[ProfessionResponse])
def list_professions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Liste toutes les professions disponibles.
    
    Accessible sans authentification.
    """
    logger.info(f"📋 Public: Liste des professions (skip={skip}, limit={limit})")
    
    professions = profession_crud.get_multi(db, skip=skip, limit=limit)
    
    logger.debug(f"   → {len(professions)} profession(s) trouvée(s)")
    return professions


@router.get("/{profession_id}", response_model=ProfessionResponse)
def get_profession(
    profession_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'une profession.
    
    Accessible sans authentification.
    """
    logger.info(f"🔍 Public: Récupération profession '{profession_id}'")
    
    profession = profession_crud.get_or_404(db, profession_id, "Profession")
    
    logger.debug(f"   → Profession '{profession_id}' récupérée")
    return profession