# app/routes/api/admin/profession.py

from http.client import HTTPException
from utils.json import load_json, save_json
from fastapi import APIRouter, Depends
from utils.roles import require_admin
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Admin - Professions"], dependencies=[Depends(require_admin)])

@router.post("/", dependencies=[Depends(require_admin)])
def create_prof(payload: dict):
    prof_id = payload.get("id")
    logger.info(f"➕ Modérateur: Création de la profession '{prof_id}'")
    
    try:
        data = load_json(config.PROFESSIONS_FILE)
        if payload["id"] in data:
            logger.warning(f"⚠️  Profession '{prof_id}' existe déjà")
            raise HTTPException(400, "Profession existe déjà")
        
        data[payload["id"]] = payload
        save_json(config.PROFESSIONS_FILE, data)
        
        logger.info(f"✅ Profession '{prof_id}' créée avec succès")
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la profession", exc_info=True)
        raise HTTPException(500, "Failed to create profession")


@router.delete("/{pid}", dependencies=[Depends(require_admin)])
def delete_prof(pid: str):
    logger.info(f"🗑️  Modérateur: Suppression de la profession '{pid}'")
    
    try:
        data = load_json(config.PROFESSIONS_FILE)
        if pid not in data:
            logger.warning(f"⚠️  Profession '{pid}' non trouvée")
            raise HTTPException(404)
        
        del data[pid]
        save_json(config.PROFESSIONS_FILE, data)
        
        logger.info(f"✅ Profession '{pid}' supprimée avec succès")
        return {"status": "deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de la profession", exc_info=True)
        raise HTTPException(500, "Failed to delete profession")