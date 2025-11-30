# app/routes/api/user/devices.py

from fastapi import APIRouter, Depends, HTTPException
from utils.roles import require_player
from utils.json import load_json, save_json
from utils.logger import get_logger
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/devices", tags=["Users - Devices"], dependencies=[Depends(require_player)])

@router.get("/")
def list_devices(user=Depends(require_player)):
    uid = user["id"]
    logger.info(f"📱 Liste des devices pour user_id={uid}")
    
    try:
        data = load_json(config.USERS_FILE)
        devices = data[uid].get("devices", [])
        logger.debug(f"   → {len(devices)} device(s) trouvé(s)")
        return {"devices": devices}
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des devices", exc_info=True)
        raise HTTPException(500, "Failed to retrieve devices")

@router.post("/add")
def add_device(device_id: str, user=Depends(require_player)):
    uid = user["id"]
    logger.info(f"➕ Ajout du device {device_id} pour user_id={uid}")
    
    try:
        data = load_json(config.USERS_FILE)
        devices = data[uid].setdefault("devices", [])

        if device_id in devices:
            logger.warning(f"⚠️  Device {device_id} déjà enregistré")
            raise HTTPException(400, "Device already registered")

        devices.append(device_id)
        save_json(config.USERS_FILE, data)
        
        logger.info(f"✅ Device {device_id} ajouté avec succès")
        return {"status": "added", "devices": devices}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout du device", exc_info=True)
        raise HTTPException(500, "Failed to add device")