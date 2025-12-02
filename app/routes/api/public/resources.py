# app/routes/api/public/resources.py
"""
Routes publiques pour les ressources (lecture seule).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from utils.logger import get_logger
from utils.db_crud import resource_crud
from database.connection import get_db
from schemas.resource import ResourceResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Public - Resources"])


@router.get("/", response_model=List[ResourceResponse])
def list_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    type: str = Query(None, description="Filtrer par type"),
    db: Session = Depends(get_db)
):
    """
    Liste toutes les ressources disponibles.
    
    Accessible sans authentification.
    """
    logger.info(f"📋 Public: Liste des ressources (skip={skip}, limit={limit}, type={type})")
    
    filters = {}
    if type:
        filters["type"] = type
    
    resources = resource_crud.get_multi(db, skip=skip, limit=limit, filters=filters)
    
    logger.debug(f"   → {len(resources)} ressource(s) trouvée(s)")
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'une ressource.
    
    Accessible sans authentification.
    """
    logger.info(f"🔍 Public: Récupération ressource '{resource_id}'")
    
    resource = resource_crud.get_or_404(db, resource_id, "Resource")
    
    logger.debug(f"   → Ressource '{resource_id}' récupérée")
    return resource