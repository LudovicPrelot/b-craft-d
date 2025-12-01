# app/routes/api/user/stats.py

from fastapi import APIRouter, Depends, HTTPException
from utils.roles import require_user
from utils.feature_flags import require_feature
from utils.logger import get_logger
from services.xp_service import add_xp, xp_for_level
from models.user import User
from utils.json import load_json, save_json
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/stats", tags=["Users - Stats"], dependencies=[Depends(require_feature("enable_stats")), Depends(require_user)]
)

@router.get("/")
def get_stats(current=Depends(require_user)):
    logger.info(f"📊 Récupération des stats pour user_id={current.get('id')}")
    
    try:
        next_level = xp_for_level(current["level"])
        
        stats_data = {
            "xp": current["xp"],
            "level": current["level"],
            "stats": current["stats"],
            "next_level_xp": next_level
        }
        
        logger.debug(f"   → Level {current['level']}, XP: {current['xp']}/{next_level}")
        return stats_data
        
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des stats", exc_info=True)
        raise HTTPException(500, "Failed to retrieve stats")

@router.post("/add_xp")
def add_xp_to_user(amount: int, current=Depends(require_user)):
    logger.info(f"⭐ Ajout de {amount} XP pour user_id={current.get('id')}")
    
    try:
        users = load_json(config.USERS_FILE)
        user = User.from_dict(current)
        
        old_level = user.level
        old_xp = user.xp
        
        add_xp(user, amount)
        
        users[user.id] = user.to_dict()
        save_json(config.USERS_FILE, users)
        
        if user.level > old_level:
            logger.info(f"✅ {amount} XP ajoutée + Level up! {old_level} → {user.level} (XP: {old_xp} → {user.xp})")
        else:
            logger.info(f"✅ {amount} XP ajoutée (Level: {user.level}, XP: {old_xp} → {user.xp})")
        
        return {"xp": user.xp, "level": user.level, "stats": user.stats}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout d'XP", exc_info=True)
        raise HTTPException(500, "Failed to add XP")