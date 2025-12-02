# app/routes/api/admin/features.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from utils.logger import get_logger
from utils.roles import require_admin
from utils.feature_flags import get_all_features_status
from database.connection import get_db
from utils.settings import toggle_feature

logger = get_logger(__name__)

router = APIRouter(
    prefix="/features", 
    tags=["Admin - Features"], 
    dependencies=[Depends(require_admin)]
)

@router.get("/")
def list_features(db: Session = Depends(get_db)):
    """Liste toutes les features et leur état."""
    return get_all_features_status(db)

@router.post("/{feature_name}/toggle")
def toggle_feature_endpoint(
    feature_name: str,
    db: Session = Depends(get_db)
):
    """Active/désactive une feature."""
    new_state = toggle_feature(db, feature_name)
    return {
        "feature": feature_name,
        "enabled": new_state
    }