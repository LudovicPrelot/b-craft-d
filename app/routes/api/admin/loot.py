# app/routes/api/admin/users.py

from fastapi import APIRouter, HTTPException, Depends
from utils.roles import require_admin
from utils.logger import get_logger
import config
import json

logger = get_logger(__name__)

router = APIRouter(prefix="/loot", tags=["Admin - Loot"], dependencies=[Depends(require_admin)])

# helper
def _load_loot():
    try:
        return json.loads(config.LOOT_TABLES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_loot(d):
    config.LOOT_TABLES_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.LOOT_TABLES_FILE.write_text(json.dumps(d, indent=4, ensure_ascii=False), encoding="utf-8")

@router.get("/tables")
def list_loot_tables():
    logger.info("🎲 Admin: Liste des loot tables")
    try:
        tables = _load_loot()
        logger.debug(f"   → {len(tables)} table(s) de loot trouvée(s)")
        return tables
    except Exception as e:
        logger.error("❌ Erreur lors de la récupération des loot tables", exc_info=True)
        raise HTTPException(500, "Failed to retrieve loot tables")

@router.post("/tables")
def create_or_update_loot_table(payload: dict):
    key = payload.get("key")
    
    if not key:
        logger.warning("⚠️  Clé manquante pour la loot table")
        raise HTTPException(400, "key missing")
    
    logger.info(f"💾 Admin: Sauvegarde de la loot table '{key}'")
    
    try:
        d = _load_loot()
        d[key] = {
            "biomes": payload.get("biomes", []),
            "table": payload.get("table", [])
        }
        _save_loot(d)
        logger.info(f"✅ Loot table '{key}' sauvegardée avec succès")
        return {"status":"saved", "key": key}
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la sauvegarde de la loot table '{key}'", exc_info=True)
        raise HTTPException(500, "Failed to save loot table")

@router.delete("/tables/{key}")
def delete_loot_table(key: str):
    logger.info(f"🗑️  Admin: Suppression de la loot table '{key}'")
    
    try:
        d = _load_loot()
        if key not in d:
            logger.warning(f"⚠️  Loot table '{key}' non trouvée")
            raise HTTPException(404)
        del d[key]
        _save_loot(d)
        logger.info(f"✅ Loot table '{key}' supprimée avec succès")
        return {"status": "deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de la loot table '{key}'", exc_info=True)
        raise HTTPException(500, "Failed to delete loot table")