# app/routes/api/user/professions.py

from fastapi import APIRouter, Depends
from utils.roles import require_user
from utils.logger import get_logger
from utils.crud import list_all, get_one
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Users - Professions"], dependencies=[Depends(require_user)])

@router.get("/")
def list_professions(current=Depends(require_user)):
    user_id = current.get("id")
    return list_all(config.PROFESSIONS_FILE, "professions", logger, user_id=user_id)

@router.get("/{profession_id}")
def get_profession(profession_id: str, current=Depends(require_user)):
    user_id = current.get("id")
    return get_one(config.PROFESSIONS_FILE, profession_id, "profession", logger, user_id=user_id)