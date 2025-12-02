# app/routes/api/user/resources.py
"""
Routes user pour les ressources.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from utils.roles import require_user
from utils.logger import get_logger
from utils.db_crud import resource_crud
from database.connection import get_db
from schemas.resource import ResourceResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Users - Resources"], dependencies=[Depends(require_user)])


@router.get("/", response_model=List[ResourceResponse])
def list_resources(
    type: str = Query(None),
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """Liste toutes les ressources."""
    user_id = current.get("id")
    logger.info(f"📋 User {user_id}: Liste des ressources (type={type})")
    
    filters = {}
    if type:
        filters["type"] = type
    
    resources = resource_crud.get_multi(db, limit=500, filters=filters)
    
    logger.debug(f"   → {len(resources)} ressource(s)")
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: str,
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """Récupère une ressource."""
    user_id = current.get("id")
    logger.info(f"🔍 User {user_id}: Récupération ressource '{resource_id}'")
    
    resource = resource_crud.get_or_404(db, resource_id, "Resource")
    
    return resource