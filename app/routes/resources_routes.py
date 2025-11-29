# app/routes/resources_routes.py

from fastapi import APIRouter, Depends, HTTPException
from utils.json import load_json, save_json
from utils.roles import require_player
from utils.roles import require_moderator
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/")
def list_resources(current=Depends(require_player)):
    logger.info(f"📦 Liste des ressources pour user_id={current.get('id')}")
    try:
        resources = list(load_json(config.RESOURCES_FILE).values())
        logger.debug(f"   → {len(resources)} ressource(s) disponible(s)")
        return resources
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des ressources", exc_info=True)
        raise HTTPException(500, "Failed to retrieve resources")


@router.post("/", dependencies=[Depends(require_moderator)])
def create_resource(payload):
    resource_id = payload.get("id")
    logger.info(f"➕ Modérateur: Création de la ressource '{resource_id}'")
    
    try:
        data = load_json(config.RESOURCES_FILE)
        if payload["id"] in data:
            logger.warning(f"⚠️  Ressource '{resource_id}' existe déjà")
            raise HTTPException(400, "Resource already exists")
        
        data[payload["id"]] = payload
        save_json(config.RESOURCES_FILE, data)
        
        logger.info(f"✅ Ressource '{resource_id}' créée avec succès")
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la ressource", exc_info=True)
        raise HTTPException(500, "Failed to create resource")


@router.delete("/{rid}", dependencies=[Depends(require_moderator)])
def delete_resource(rid: str):
    logger.info(f"🗑️  Modérateur: Suppression de la ressource '{rid}'")
    
    try:
        data = load_json(config.RESOURCES_FILE)
        if rid not in data:
            logger.warning(f"⚠️  Ressource '{rid}' non trouvée")
            raise HTTPException(404, "Resource not found")
        
        del data[rid]
        save_json(config.RESOURCES_FILE, data)
        
        logger.info(f"✅ Ressource '{rid}' supprimée avec succès")
        return {"status": "deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de la ressource", exc_info=True)
        raise HTTPException(500, "Failed to delete resource")