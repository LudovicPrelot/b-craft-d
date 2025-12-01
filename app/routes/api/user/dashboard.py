# app/routes/api/user/dashboard.py

from fastapi import APIRouter, Depends
from utils.deps import get_current_user_required
from utils.roles import require_user
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Users - Dashboard"], dependencies=[Depends(require_user)])

@router.get("/")
def user_dashboard(user=Depends(get_current_user_required)):
    """
    Renvoie les informations de base du joueur connecté.
    """
    user = dict(user)
    user.pop("password_hash", None)
    return {"user": user}
