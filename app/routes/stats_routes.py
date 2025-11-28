# routes/stats_routes.py

from fastapi import APIRouter, Depends
from utils.deps import require_user
from utils.feature_flags import require_feature
from services.xp_service import add_xp, xp_for_level
from models.user import User
from utils.storage import load_json, save_json
import config

router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
    dependencies=[Depends(require_feature("enable_stats"))]  # <--- feature flag
)

@router.get("/")
def get_stats(current=Depends(require_user)):
    return {
        "xp": current["xp"],
        "level": current["level"],
        "stats": current["stats"],
        "next_level_xp": xp_for_level(current["level"])
    }

@router.post("/add_xp")
def add_xp_to_user(amount: int, current=Depends(require_user)):
    users = load_json(config.USERS_FILE)
    user = User.from_dict(current)

    add_xp(user, amount)

    users[user.id] = user.to_dict()
    save_json(config.USERS_FILE, users)

    return {"xp": user.xp, "level": user.level, "stats": user.stats}
