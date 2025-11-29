# routes/resources_routes.py

from fastapi import APIRouter, Depends, HTTPException
from utils.json import load_json, save_json
from utils.roles import require_player
from utils.roles import require_moderator
import config

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/")
def list_resources(current=Depends(require_player)):
    return list(load_json(config.RESOURCES_FILE).values())


@router.post("/", dependencies=[Depends(require_moderator)])
def create_resource(payload):
    data = load_json(config.RESOURCES_FILE)
    if payload["id"] in data:
        raise HTTPException(400)
    data[payload["id"]] = payload
    save_json(config.RESOURCES_FILE, data)
    return payload


@router.delete("/{rid}", dependencies=[Depends(require_moderator)])
def delete_resource(rid: str):
    data = load_json(config.RESOURCES_FILE)
    if rid not in data:
        raise HTTPException(404)
    del data[rid]
    save_json(config.RESOURCES_FILE, data)
    return {"status": "deleted"}
