# app/routes/api/user/resources.py

from fastapi import APIRouter, Depends
from utils.roles import require_user
from utils.logger import get_logger
from utils.crud import list_all, get_one
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Users - Resources"], dependencies=[Depends(require_user)])

@router.get("/")
def list_resources(current=Depends(require_user)):
    user_id = current.get("id")
    return list_all(config.RESOURCES_FILE, "resources", logger, user_id=user_id)

@router.get("/{resource_id}")
def get_resource(resource_id: str, current=Depends(require_user)):
    user_id = current.get("id")
    return get_one(config.RESOURCES_FILE, resource_id, "resource", logger, user_id=user_id)