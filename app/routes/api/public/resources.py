# app/routes/api/public/resources.py

from fastapi import APIRouter
from utils.logger import get_logger
from utils.crud import list_all
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Public - Resources"])

@router.get("/")
def list_resources():
    items = list_all(config.RESOURCES_FILE, "resources", logger)
    return {"resources": items}  # Format public avec clé