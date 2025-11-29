# routes/admin_settings_routes.py

from fastapi import APIRouter, Depends
from utils.roles import require_admin
from utils.settings import get_settings, update_settings

router = APIRouter(
    prefix="/admin/settings",
    tags=["Admin Settings"],
    dependencies=[Depends(require_admin)]
)

@router.get("/")
def read_settings():
    return get_settings()

@router.post("/")
def write_settings(settings: dict):
    update_settings(settings)
    return {"status": "saved", "settings": settings}
