# app/routes/api/admin/resources.py
"""
Routes Admin pour la gestion des ressources - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from utils.roles import require_admin
from utils.logger import get_logger
from utils.db_crud import resource_crud
from database.connection import get_db
from models import Resource
from schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse

logger = get_logger(__name__)

router = APIRouter(
    prefix="/resources", 
    tags=["Admin - Resources"], 
    dependencies=[Depends(require_admin)]
)


# ============================================================================
# ROUTES CRUD
# ============================================================================

@router.get("/", response_model=List[ResourceResponse])
def list_resources(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=500, description="Nombre max d'éléments à retourner"),
    type: str = Query(None, description="Filtrer par type de ressource"),
    db: Session = Depends(get_db)
):
    """
    Liste toutes les ressources avec pagination.
    
    - **skip**: Pagination - nombre d'éléments à sauter
    - **limit**: Pagination - nombre max d'éléments (max 500)
    - **type**: Filtre optionnel par type (mineral, metal, food, etc.)
    """
    logger.info(f"📋 Admin: Liste des ressources (skip={skip}, limit={limit}, type={type})")
    
    # Filtres optionnels
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
    Récupère une ressource par son ID.
    
    - **resource_id**: Identifiant unique de la ressource
    """
    logger.info(f"🔍 Admin: Récupération ressource '{resource_id}'")
    
    resource = resource_crud.get_or_404(db, resource_id, "Resource")
    
    logger.debug(f"   → Ressource '{resource_id}' récupérée")
    return resource


@router.post("/", response_model=ResourceResponse, status_code=201)
def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle ressource.
    
    - **id**: Identifiant unique (utilisé dans les recettes et inventaires)
    - **name**: Nom affiché de la ressource
    - **type**: Type de ressource (mineral, metal, food, material, etc.)
    - **description**: Description détaillée (optionnel)
    - **weight**: Poids unitaire en kg (défaut: 1.0)
    - **stack_size**: Taille max d'un stack (défaut: 999)
    """
    logger.info(f"➕ Admin: Création ressource '{resource.id}'")
    
    # Vérifie que l'ID n'existe pas déjà
    existing = resource_crud.get(db, resource.id)
    if existing:
        logger.warning(f"⚠️  Ressource '{resource.id}' existe déjà")
        raise HTTPException(400, f"Resource '{resource.id}' already exists")
    
    # Validation métier
    if resource.weight < 0:
        raise HTTPException(400, "Weight cannot be negative")
    
    if resource.stack_size < 1:
        raise HTTPException(400, "Stack size must be at least 1")
    
    # Crée la ressource
    new_resource = resource_crud.create(db, obj_in=resource.model_dump())
    
    logger.info(f"✅ Ressource '{resource.id}' créée avec succès")
    return new_resource


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: str,
    resource: ResourceUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une ressource existante.
    
    Seuls les champs fournis seront mis à jour.
    """
    logger.info(f"✏️  Admin: Mise à jour ressource '{resource_id}'")
    
    # Filtre les champs None (non fournis)
    update_data = resource.model_dump(exclude_unset=True)
    
    if not update_data:
        logger.warning(f"⚠️  Aucun champ à mettre à jour pour '{resource_id}'")
        raise HTTPException(400, "No fields to update")
    
    logger.debug(f"   → Champs à mettre à jour: {list(update_data.keys())}")
    
    # Validation métier
    if "weight" in update_data and update_data["weight"] < 0:
        raise HTTPException(400, "Weight cannot be negative")
    
    if "stack_size" in update_data and update_data["stack_size"] < 1:
        raise HTTPException(400, "Stack size must be at least 1")
    
    updated = resource_crud.update_by_id(db, id=resource_id, obj_in=update_data)
    
    logger.info(f"✅ Ressource '{resource_id}' mise à jour")
    return updated


@router.delete("/{resource_id}")
def delete_resource(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """
    Supprime une ressource.
    
    ⚠️ Attention: Cette action est irréversible.
    Vérifie d'abord qu'aucune recette n'utilise cette ressource.
    """
    logger.info(f"🗑️  Admin: Suppression ressource '{resource_id}'")
    
    # TODO: Vérifier qu'aucune recette n'utilise cette ressource
    # (nécessite une requête sur la table recipes)
    
    resource_crud.delete(db, id=resource_id)
    
    logger.info(f"✅ Ressource '{resource_id}' supprimée")
    return {"status": "deleted", "id": resource_id}


# ============================================================================
# ROUTES CUSTOM / STATS
# ============================================================================

@router.get("/stats/by-type")
def resources_stats_by_type(db: Session = Depends(get_db)):
    """
    Statistiques: nombre de ressources par type.
    
    Retourne un dictionnaire {type: count}
    """
    logger.info("📊 Admin: Stats ressources par type")
    
    from sqlalchemy import func
    
    result = (
        db.query(Resource.type, func.count(Resource.id))
        .group_by(Resource.type)
        .all()
    )
    
    stats = {type_name: count for type_name, count in result}
    
    logger.debug(f"   → {len(stats)} type(s) de ressources")
    return stats


@router.get("/search/{query}")
def search_resources(
    query: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Recherche de ressources par nom ou description.
    
    Effectue une recherche insensible à la casse.
    """
    logger.info(f"🔍 Admin: Recherche ressources '{query}'")
    
    results = (
        db.query(Resource)
        .filter(
            (Resource.name.ilike(f"%{query}%")) | 
            (Resource.description.ilike(f"%{query}%"))
        )
        .limit(limit)
        .all()
    )
    
    logger.debug(f"   → {len(results)} résultat(s)")
    return [r.to_dict() for r in results]