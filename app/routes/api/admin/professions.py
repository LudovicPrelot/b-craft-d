# app/routes/api/admin/professions.py

from fastapi import APIRouter, Depends, Body
from utils.roles import require_admin
from utils.logger import get_logger
from utils.crud import list_all, get_one, create_one, update_one, delete_one
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Admin - Professions"], dependencies=[Depends(require_admin)])

@router.get("/")
def list_professions():
    return list_all(config.PROFESSIONS_FILE, "professions", logger)

@router.get("/{profession_id}")
def get_profession(profession_id: str):
    return get_one(config.PROFESSIONS_FILE, profession_id, "profession", logger)

@router.post("/")
def create_profession(payload: dict = Body(...)):
    return create_one(config.PROFESSIONS_FILE, payload, "profession", logger)

@router.put("/{profession_id}")
def update_profession(profession_id: str, payload: dict = Body(...)):
    return update_one(config.PROFESSIONS_FILE, profession_id, payload, "profession", logger)

@router.delete("/{profession_id}")
def delete_profession(profession_id: str):
    return delete_one(config.PROFESSIONS_FILE, profession_id, "profession", logger)

@router.post("/{profession_id}/add_resource")
def add_resource_to_profession(profession_id: str, resource_id: str = Body(..., embed=True)):
    """Exemple de route custom avec logique spécifique"""
    logger.info(f"➕ Ajout ressource '{resource_id}' à profession '{profession_id}'")
    
    # Récupère la profession
    profession = get_one(config.PROFESSIONS_FILE, profession_id, "profession", logger)
    
    # Logique custom
    if "resources_found" not in profession:
        profession["resources_found"] = []
    
    if resource_id not in profession["resources_found"]:
        profession["resources_found"].append(resource_id)
    
    # Mise à jour
    return update_one(config.PROFESSIONS_FILE, profession_id, profession, "profession", logger, merge=False)  # Remplacement complet