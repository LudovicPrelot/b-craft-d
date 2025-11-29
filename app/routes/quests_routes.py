# routes/quests_routes.py

from fastapi import APIRouter, Depends, HTTPException
from utils.roles import require_player
from utils.feature_flags import require_feature
from utils.json import load_json, save_json
from models.user import User
from services.xp_service import add_xp
import config

router = APIRouter(
    prefix="/quests",
    tags=["Quests"],
    dependencies=[Depends(require_feature("enable_quests"))]  # <--- feature flag
)


@router.get("/")
def list_quests():
    return load_json(config.QUESTS_FILE)


@router.post("/complete/{quest_id}")
def complete_quest(quest_id: str, current=Depends(require_player)):
    quests = load_json(config.QUESTS_FILE)
    users = load_json(config.USERS_FILE)

    if quest_id not in quests:
        raise HTTPException(404, "Quest not found")

    quest = quests[quest_id]
    user = User.from_dict(current)

    req_collect = quest.get("requirements", {}).get("collect", {})

    # Check requirements
    for item, qty in req_collect.items():
        if user.inventory.get(item, 0) < qty:
            return {"status": "not_enough_items", "missing": {item: qty}}

    # Remove items
    for item, qty in req_collect.items():
        user.inventory[item] -= qty
        if user.inventory[item] <= 0:
            del user.inventory[item]

    # Apply reward
    reward = quest["reward"]

    if "xp" in reward:
        add_xp(user, reward["xp"])

    if "items" in reward:
        for item, qty in reward["items"].items():
            user.inventory[item] = user.inventory.get(item, 0) + qty

    # save
    users[user.id] = user.to_dict()
    save_json(config.USERS_FILE, users)

    return {
        "status": "completed",
        "reward": reward,
        "level": user.level,
        "xp": user.xp
    }
