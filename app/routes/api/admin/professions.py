# app/routes/api/admin/professions.py (VERSION POSTGRESQL)

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import List

from utils.roles import require_admin
from utils.logger import get_logger
from utils.db_crud import profession_crud
from database.connection import get_db
from schemas.profession import ProfessionResponse, ProfessionCreate, ProfessionUpdate

logger = get_logger(__name__)

router = APIRouter(
    prefix="/professions", 
    tags=["Admin - Professions"], 
    dependencies=[Depends(require_admin)]
)


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/", response_model=List[ProfessionResponse])
def list_professions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Liste toutes les professions avec pagination."""
    logger.info(f"📋 Admin: Liste des professions (skip={skip}, limit={limit})")
    
    professions = profession_crud.get_multi(db, skip=skip, limit=limit)
    
    logger.debug(f"   → {len(professions)} profession(s) trouvée(s)")
    return professions


@router.get("/{profession_id}", response_model=ProfessionResponse)
def get_profession(
    profession_id: str,
    db: Session = Depends(get_db)
):
    """Récupère une profession par son ID."""
    logger.info(f"🔍 Admin: Récupération profession '{profession_id}'")
    
    profession = profession_crud.get_or_404(db, profession_id, "Profession")
    
    logger.debug(f"   → Profession '{profession_id}' récupérée")
    return profession


@router.post("/", response_model=ProfessionResponse, status_code=201)
def create_profession(
    profession: ProfessionCreate,
    db: Session = Depends(get_db)
):
    """Crée une nouvelle profession."""
    logger.info(f"➕ Admin: Création profession '{profession.id}'")
    
    # Vérifie que l'ID n'existe pas déjà
    existing = profession_crud.get(db, profession.id)
    if existing:
        logger.warning(f"⚠️  Profession '{profession.id}' existe déjà")
        from fastapi import HTTPException
        raise HTTPException(400, f"Profession '{profession.id}' already exists")
    
    # Crée la profession
    new_profession = profession_crud.create(db, obj_in=profession.model_dump())
    
    logger.info(f"✅ Profession '{profession.id}' créée avec succès")
    return new_profession


@router.put("/{profession_id}", response_model=ProfessionResponse)
def update_profession(
    profession_id: str,
    profession: ProfessionUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une profession existante."""
    logger.info(f"✏️  Admin: Mise à jour profession '{profession_id}'")
    
    # Filtre les champs None (non fournis)
    update_data = profession.model_dump(exclude_unset=True)
    
    logger.debug(f"   → Champs à mettre à jour: {list(update_data.keys())}")
    
    updated = profession_crud.update_by_id(db, id=profession_id, obj_in=update_data)
    
    logger.info(f"✅ Profession '{profession_id}' mise à jour")
    return updated


@router.delete("/{profession_id}")
def delete_profession(
    profession_id: str,
    db: Session = Depends(get_db)
):
    """Supprime une profession."""
    logger.info(f"🗑️  Admin: Suppression profession '{profession_id}'")
    
    profession_crud.delete(db, id=profession_id)
    
    logger.info(f"✅ Profession '{profession_id}' supprimée")
    return {"status": "deleted", "id": profession_id}


# ============================================================================
# ROUTES CUSTOM (spécifiques métier)
# ============================================================================

@router.post("/{profession_id}/add_resource")
def add_resource_to_profession(
    profession_id: str,
    resource_id: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Ajoute une ressource trouvable à une profession."""
    logger.info(f"➕ Ajout ressource '{resource_id}' à profession '{profession_id}'")
    
    # Récupère la profession
    profession = profession_crud.get_or_404(db, profession_id, "Profession")
    
    # Ajoute la ressource si pas déjà présente
    if resource_id not in profession.resources_found:
        profession.resources_found.append(resource_id)
        db.commit()
        db.refresh(profession)
        
        logger.info(f"✅ Ressource '{resource_id}' ajoutée")
    else:
        logger.debug(f"   → Ressource '{resource_id}' déjà présente")
    
    return profession.to_dict()