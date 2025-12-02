# app/routes/api/public/quests.py
"""
Routes publiques pour les quêtes - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from utils.logger import get_logger
from utils.feature_flags import require_feature
from utils.db_crud import quest_crud
from database.connection import get_db

logger = get_logger(__name__)

router = APIRouter(
    prefix="/quests", 
    tags=["Public - Quests"],
    dependencies=[Depends(require_feature("enable_quests"))]
)


@router.get("/")
def list_quests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Liste toutes les quêtes disponibles."""
    logger.info(f"📜 Public: Liste des quêtes")
    
    try:
        quests = quest_crud.get_multi(db, skip=skip, limit=limit)
        result = [q.to_dict() for q in quests]
        
        logger.debug(f"   → {len(result)} quête(s)")
        return result
        
    except Exception as e:
        logger.error("❌ Erreur récupération quêtes", exc_info=True)
        raise


@router.get("/{quest_id}")
def get_quest(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Récupère une quête spécifique."""
    logger.info(f"🔍 Public: Récupération quête '{quest_id}'")
    
    quest = quest_crud.get_or_404(db, quest_id, "Quest")
    return quest.to_dict()