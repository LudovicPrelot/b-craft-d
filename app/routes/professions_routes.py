# routes/professions_routes.py

from fastapi import APIRouter, Depends, HTTPException
from utils.deps import require_user
from utils.roles import require_role_moderator
from utils.storage import load_json, save_json
import config

router = APIRouter(prefix="/professions", tags=["Professions"])


@router.get("/")
def list_professions(current=Depends(require_user)):
    return list(load_json(config.PROFESSIONS_FILE).values())


@router.post("/", dependencies=[Depends(require_role_moderator)])
def create_prof(payload: dict):
    data = load_json(config.PROFESSIONS_FILE)
    if payload["id"] in data:
        raise HTTPException(400, "Profession existe déjà")
    data[payload["id"]] = payload
    save_json(config.PROFESSIONS_FILE, data)
    return payload


@router.delete("/{pid}", dependencies=[Depends(require_role_moderator)])
def delete_prof(pid: str):
    data = load_json(config.PROFESSIONS_FILE)
    if pid not in data:
        raise HTTPException(404)
    del data[pid]
    save_json(config.PROFESSIONS_FILE, data)
    return {"status": "deleted"}
