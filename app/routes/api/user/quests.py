# app/routes/api/user/quests.py
"""
Routes user pour les quêtes - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils.roles import require_user
from utils.feature_flags import require_feature
from utils.logger import get_logger
from utils.db_crud import quest_crud, user_crud
from database.connection import get_db
from services.xp_service import add_xp

logger_user = get_logger(__name__)

router = APIRouter(
    prefix="/quests", 
    tags=["Users - Quests"],
    dependencies=[
        Depends(require_feature("enable_quests")),
        Depends(require_user)
    ]
)


@router.post("/complete/{quest_id}")
def complete_quest(
    quest_id: str,
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Complète une quête.
    
    Process:
    1. Vérifie conditions (niveau, profession)
    2. Vérifie requirements (items collectés)
    3. Retire les items requis
    4. Donne les rewards (XP, items)
    5. Vérifie level up
    """
    user_id = current.get("id")
    logger_user.info(f"🎯 Completion quête '{quest_id}' par user={user_id}")
    
    try:
        # Récupère quête et user
        quest = quest_crud.get_or_404(db, quest_id, "Quest")
        user = user_crud.get_or_404(db, user_id, "User")
        
        # Vérifications niveau
        if quest.required_level > user.level:
            logger_user.warning(f"⚠️  Niveau insuffisant: requis={quest.required_level}, actuel={user.level}")
            raise HTTPException(400, f"Niveau {quest.required_level} requis")
        
        # Vérifications profession
        if quest.required_profession and quest.required_profession != user.profession:
            logger_user.warning(f"⚠️  Profession incorrecte")
            raise HTTPException(400, f"Profession '{quest.required_profession}' requise")
        
        # Vérifications requirements (collect)
        req_collect = quest.requirements.get("collect", {})
        
        logger_user.debug(f"   → Vérification requirements: {req_collect}")
        
        for item, qty in req_collect.items():
            if user.inventory.get(item, 0) < qty:
                logger_user.warning(f"⚠️  Items insuffisants: {item} (requis: {qty}, possédé: {user.inventory.get(item, 0)})")
                return {
                    "status": "not_enough_items",
                    "missing": {item: qty - user.inventory.get(item, 0)}
                }
        
        # Retire les items
        logger_user.debug(f"   → Retrait des items requis")
        for item, qty in req_collect.items():
            user.inventory[item] -= qty
            if user.inventory[item] <= 0:
                del user.inventory[item]
        
        # Applique rewards
        rewards = quest.rewards or {}
        logger_user.debug(f"   → Application rewards: {rewards}")
        
        old_level = user.level
        
        # XP
        if "xp" in rewards:
            add_xp(user, rewards["xp"])
        
        # Items
        if "items" in rewards:
            for item, qty in rewards["items"].items():
                user.inventory[item] = user.inventory.get(item, 0) + qty
        
        # Commit
        db.commit()
        db.refresh(user)
        
        level_up = user.level > old_level
        
        if level_up:
            logger_user.info(f"   🎉 Level up! {old_level} → {user.level}")
        
        logger_user.info(f"✅ Quête '{quest_id}' complétée")
        
        return {
            "status": "completed",
            "reward": rewards,
            "level": user.level,
            "xp": user.xp,
            "level_up": level_up,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger_user.error(f"❌ Erreur completion quête", exc_info=True)
        raise HTTPException(500, "Failed to complete quest")