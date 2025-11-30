# app/routes/api/public/professions.py

from fastapi import APIRouter
from utils.logger import get_logger
from utils.crud import list_all
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/professions", tags=["Public - Professions"])

@router.get("/")
def list_professions():
    items = list_all(config.PROFESSIONS_FILE, "professions", logger)
    return {"professions": items}  # Format public avec clé