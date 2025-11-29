# app/routes/professions_routes.py

from fastapi import APIRouter, Depends, HTTPException
from utils.roles import require_player
from utils.roles import require_moderator
from utils.json import load_json, save_json
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Professions"])


@router.get("/")
def list_professions(current=Depends(require_player)):
    logger.info(f"👷 Liste des professions pour user_id={current.get('id')}")
    try:
        professions = list(load_json(config.PROFESSIONS_FILE).values())
        logger.debug(f"   → {len(professions)} profession(s) disponible(s)")
        return professions
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des professions", exc_info=True)
        raise HTTPException(500, "Failed to retrieve professions")


@router.post("/", dependencies=[Depends(require_moderator)])
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


@router.delete("/{pid}", dependencies=[Depends(require_moderator)])
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