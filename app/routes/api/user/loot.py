# app/routes/api/user/loot.py

from fastapi import APIRouter, Depends, Query, HTTPException
from utils.roles import require_user
from utils.json import load_json, save_json
from utils.feature_flags import require_feature
from utils.logger import get_logger
from models.user import User
from services.xp_service import add_xp
import config, random
from collections import defaultdict
from pathlib import Path
import json

logger = get_logger(__name__)

router = APIRouter(prefix="/loot", tags=["Users - Loot"], dependencies=[Depends(require_feature("enable_loot"))]
)

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def weighted_choice(entries):
    total = sum(w for _, w in entries)
    r = random.uniform(0, total)
    upto = 0
    for entry, weight in entries:
        if upto + weight >= r:
            return entry
        upto += weight
    return entries[-1][0]


def load_environment_modifiers():
    path = config.LOOT_ENVIRONMENT_FILE
    if not path.exists():
        return {"season_modifiers": {}, "weather_modifiers": {}, "event_modifiers": {}}
    return json.loads(path.read_text(encoding="utf-8"))


RARITY_MULTIPLIERS = {
    "common": 1.0,
    "uncommon": 0.8,
    "rare": 0.5,
    "legendary": 0.2
}

STAT_MULTIPLIERS = {
    "strength": 0.03,
    "agility": 0.02,
    "endurance": 0.01
}


# -------------------------------------------------------
# Main Loot Route
# -------------------------------------------------------

@router.post("/collect")
def collect(current=Depends(require_user), attempts: int = Query(1, ge=1, le=10), season: str = Query("summer"), weather: str = Query("sunny"), event: str = Query(None)):
    """
    Loot system with:
    - Biomes
    - Seasons
    - Weather
    - Rare events
    - Stat-based weighted loot
    - Feature flag protection
    """

    user = User.from_dict(current)
    logger.info(f"🎲 Collecte de loot par user_id={user.id} (attempts={attempts}, season={season}, weather={weather})")
    
    try:
        users = load_json(config.USERS_FILE)
        loot_tables = load_json(config.LOOT_TABLES_FILE)
        env_mod = load_environment_modifiers()

        # choose available loot tables
        tables = []

        if user.biome and user.biome in loot_tables:
            tables.append(loot_tables[user.biome])
            logger.debug(f"   → Table de loot pour biome '{user.biome}' ajoutée")

        # job-based fallback
        professions = load_json(config.PROFESSIONS_FILE)
        prof = professions.get(user.profession, {})
        for b in prof.get("biomes", []):
            if b in loot_tables:
                tables.append(loot_tables[b])
                logger.debug(f"   → Table de loot profession '{b}' ajoutée")

        # default table
        if "default" in loot_tables:
            tables.append(loot_tables["default"])
            logger.debug(f"   → Table de loot par défaut ajoutée")

        if not tables:
            logger.warning(f"⚠️  Aucune table de loot disponible")
            raise HTTPException(400, "No loot tables available.")

        gained = defaultdict(int)

        # modifiers
        season_mult = env_mod["season_modifiers"].get(season, 1.0)
        weather_mult = env_mod["weather_modifiers"].get(weather, 1.0)
        event_mult = 1.0 if event is None else env_mod["event_modifiers"].get(event, 1.0)
        
        logger.debug(f"   → Multiplicateurs: season={season_mult}, weather={weather_mult}, event={event_mult}")

        for _ in range(attempts):
            chosen = random.choice(tables)
            weights = []

            for e in chosen["table"]:
                rarity = e.get("rarity", "common")
                base = float(e.get("weight", 1))

                rarity_mult = RARITY_MULTIPLIERS.get(rarity, 1.0)

                stat_mult = (
                    user.stats.get("strength", 1) * STAT_MULTIPLIERS["strength"]
                    + user.stats.get("agility", 1) * STAT_MULTIPLIERS["agility"]
                    + user.stats.get("endurance", 1) * STAT_MULTIPLIERS["endurance"]
                )

                final_weight = base * rarity_mult
                final_weight *= (1.0 + stat_mult)
                final_weight *= season_mult
                final_weight *= weather_mult
                final_weight *= event_mult

                weights.append((e, max(0.01, final_weight)))

            entry = weighted_choice(weights)
            qty = random.randint(entry.get("min", 1), entry.get("max", 1))
            gained[entry["item"]] += qty

        # update user inventory
        for item, qty in gained.items():
            user.inventory[item] = user.inventory.get(item, 0) + qty

        # save
        users[user.id] = user.to_dict()
        save_json(config.USERS_FILE, users)
        
        logger.info(f"✅ Loot collecté: {dict(gained)}")

        return {
            "gained": dict(gained),
            "inventory": user.inventory,
            "multipliers": {
                "season": season_mult,
                "weather": weather_mult,
                "event": event_mult
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la collecte de loot", exc_info=True)
        raise HTTPException(500, "Failed to collect loot")