# routes/devices_routes.py

from fastapi import APIRouter, Depends, HTTPException
from utils.roles import require_player
from utils.json import load_json, save_json
import config

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.get("/")
def list_devices(user=Depends(require_player)):
    data = load_json(config.USERS_FILE)
    uid = user["id"]
    devices = data[uid].get("devices", [])
    return {"devices": devices}

@router.post("/add")
def add_device(device_id: str, user=Depends(require_player)):
    data = load_json(config.USERS_FILE)
    uid = user["id"]

    devices = data[uid].setdefault("devices", [])

    if device_id in devices:
        raise HTTPException(400, "Device already registered")

    devices.append(device_id)
    save_json(config.USERS_FILE, data)

    return {"status": "added", "devices": devices}
