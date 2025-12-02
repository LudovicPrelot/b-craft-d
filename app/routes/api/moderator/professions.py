# app/routes/api/moderator/professions.py

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import List

from utils.roles import require_moderator
from utils.logger import get_logger
from utils.db_crud import profession_crud
from database.connection import get_db
from schemas.profession import ProfessionResponse, ProfessionUpdate

logger = get_logger(__name__)


router = APIRouter(
    prefix="/professions",
    tags=["Moderator - Professions"],
    dependencies=[Depends(require_moderator)]
)


@router.get("/", response_model=List[ProfessionResponse])
def list_professions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Liste toutes les professions avec pagination."""
    logger.info(f"📋 Modérateur: Liste des professions (skip={skip}, limit={limit})")
    
    professions = profession_crud.get_multi(db, skip=skip, limit=limit)
    
    logger.debug(f"   → {len(professions)} profession(s) trouvée(s)")
    return professions


@router.get("/{profession_id}", response_model=ProfessionResponse)
def get_profession(
    profession_id: str,
    db: Session = Depends(get_db)
):
    """Récupère une profession par son ID."""
    logger.info(f"🔍 Modérateur: Récupération profession '{profession_id}'")
    
    profession = profession_crud.get_or_404(db, profession_id, "Profession")
    
    logger.debug(f"   → Profession '{profession_id}' récupérée")
    return profession


@router.put("/{profession_id}", response_model=ProfessionResponse)
def update_profession(
    profession_id: str,
    profession: ProfessionUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une profession existante."""
    logger.info(f"✏️  Modérateur: Mise à jour profession '{profession_id}'")
    
    # Filtre les champs None (non fournis)
    update_data = profession.model_dump(exclude_unset=True)
    
    logger.debug(f"   → Champs à mettre à jour: {list(update_data.keys())}")
    
    updated = profession_crud.update_by_id(db, id=profession_id, obj_in=update_data)
    
    logger.info(f"✅ Profession '{profession_id}' mise à jour")
    return updated
