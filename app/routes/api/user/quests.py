# app/routes/api/user/quests.py
from fastapi import APIRouter, Depends, HTTPException
from utils.json import load_json, save_json
from utils.logger import get_logger
from utils.feature_flags import require_feature
from utils.roles import require_player
from services.xp_service import add_xp
from models.user import User
import config

logger = get_logger(__name__)

router = APIRouter(prefix="/quests", tags=["Users - Quests"], dependencies=[Depends(require_feature("enable_quests")), Depends(require_player)])

@router.post("/complete/{quest_id}")
def complete_quest(quest_id: str, current=Depends(require_player)):
    user = User.from_dict(current)
    logger.info(f"🎯 Tentative de complétion de la quête '{quest_id}' par user_id={user.id}")
    
    try:
        quests = load_json(config.QUESTS_FILE)
        users = load_json(config.USERS_FILE)

        if quest_id not in quests:
            logger.warning(f"⚠️  Quête '{quest_id}' non trouvée")
            raise HTTPException(404, "Quest not found")

        quest = quests[quest_id]
        req_collect = quest.get("requirements", {}).get("collect", {})

        # Check requirements
        logger.debug(f"   → Vérification des prérequis: {req_collect}")
        for item, qty in req_collect.items():
            if user.inventory.get(item, 0) < qty:
                logger.warning(f"⚠️  Items insuffisants: {item} (requis: {qty}, possédé: {user.inventory.get(item, 0)})")
                return {"status": "not_enough_items", "missing": {item: qty}}

        # Remove items
        logger.debug(f"   → Retrait des items requis de l'inventaire")
        for item, qty in req_collect.items():
            user.inventory[item] -= qty
            if user.inventory[item] <= 0:
                del user.inventory[item]

        # Apply reward
        reward = quest["reward"]
        logger.debug(f"   → Application des récompenses: {reward}")

        if "xp" in reward:
            old_level = user.level
            add_xp(user, reward["xp"])
            if user.level > old_level:
                logger.info(f"   🎉 Level up! {old_level} → {user.level}")

        if "items" in reward:
            for item, qty in reward["items"].items():
                user.inventory[item] = user.inventory.get(item, 0) + qty

        # save
        users[user.id] = user.to_dict()
        save_json(config.USERS_FILE, users)

        logger.info(f"✅ Quête '{quest_id}' complétée avec succès (level: {user.level}, xp: {user.xp})")

        return {
            "status": "completed",
            "reward": reward,
            "level": user.level,
            "xp": user.xp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la complétion de la quête '{quest_id}'", exc_info=True)
        raise HTTPException(500, "Failed to complete quest")