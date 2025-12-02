# app/scripts/migrate_json_to_postgres.py
"""
Migration des données JSON vers PostgreSQL.

Usage:
    python -m scripts.migrate_json_to_postgres
"""

import sys
from pathlib import Path

# Ajoute app/ au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime, timedelta
from database.connection import SessionLocal, init_db
from models import (
    User, RefreshToken, Profession, Resource, Recipe, 
    LootTable, Quest, Setting
)
import config
from utils.logger import get_logger

logger = get_logger(__name__)


def load_json_file(path):
    """Charge un fichier JSON."""
    if not path.exists():
        logger.warning(f"⚠️  Fichier non trouvé: {path}")
        return {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Erreur lecture {path}: {e}")
        return {}


def migrate_users(db):
    """Migre users.json → table users."""
    logger.info("👥 Migration des utilisateurs...")
    
    data = load_json_file(config.USERS_FILE)
    count = 0
    
    for user_id, user_data in data.items():
        user = User(
            id=user_id,
            firstname=user_data.get("firstname", ""),
            lastname=user_data.get("lastname", ""),
            mail=user_data.get("mail", ""),
            login=user_data.get("login", ""),
            password_hash=user_data.get("password_hash", ""),
            profession=user_data.get("profession", ""),
            subclasses=user_data.get("subclasses", []),
            inventory=user_data.get("inventory", {}),
            xp=user_data.get("xp", 0),
            level=user_data.get("level", 1),
            stats=user_data.get("stats", {"strength": 1, "agility": 1, "endurance": 1}),
            biome=user_data.get("biome", ""),
            is_admin=user_data.get("is_admin", False),
            is_moderator=user_data.get("is_moderator", False),
        )
        
        db.add(user)
        count += 1
    
    db.commit()
    logger.info(f"✅ {count} utilisateurs migrés")


def migrate_refresh_tokens(db):
    """Migre refresh_tokens.json → table refresh_tokens."""
    logger.info("🔑 Migration des refresh tokens...")
    
    data = load_json_file(config.REFRESH_TOKENS_FILE)
    count = 0
    
    for token_hash, meta in data.items():
        # Calcul de expires_at depuis exp (timestamp)
        exp_timestamp = meta.get("exp")
        if not exp_timestamp:
            continue
        
        expires_at = datetime.fromtimestamp(exp_timestamp)
        
        token = RefreshToken(
            token_hash=token_hash,
            user_id=meta.get("user_id", ""),
            device_id=meta.get("device_id", ""),
            device_name=meta.get("device_name", ""),
            created_at=datetime.fromtimestamp(meta.get("created_at", 0)),
            expires_at=expires_at,
        )
        
        db.add(token)
        count += 1
    
    db.commit()
    logger.info(f"✅ {count} refresh tokens migrés")


def migrate_professions(db):
    """Migre professions.json → table professions."""
    logger.info("👷 Migration des professions...")
    
    data = load_json_file(config.PROFESSIONS_FILE)
    count = 0
    
    for prof_id, prof_data in data.items():
        profession = Profession(
            id=prof_id,
            name=prof_data.get("name", ""),
            description=prof_data.get("description", ""),
            resources_found=prof_data.get("resources_found", []),
            allowed_recipes=prof_data.get("allowed_recipes", []),
            subclasses=prof_data.get("subclasses", []),
        )
        
        db.add(profession)
        count += 1
    
    db.commit()
    logger.info(f"✅ {count} professions migrées")


def migrate_resources(db):
    """Migre resources.json → table resources."""
    logger.info("📦 Migration des ressources...")
    
    data = load_json_file(config.RESOURCES_FILE)
    count = 0
    
    for res_id, res_data in data.items():
        resource = Resource(
            id=res_id,
            name=res_data.get("name", ""),
            type=res_data.get("type", ""),
            description=res_data.get("description", ""),
            weight=res_data.get("weight", 1.0),
            stack_size=res_data.get("stack_size", 999),
        )
        
        db.add(resource)
        count += 1
    
    db.commit()
    logger.info(f"✅ {count} ressources migrées")


def migrate_recipes(db):
    """Migre recipes.json → table recipes."""
    logger.info("📜 Migration des recettes...")
    
    data = load_json_file(config.RECIPES_FILE)
    count = 0
    
    for recipe_id, recipe_data in data.items():
        recipe = Recipe(
            id=recipe_id,
            output=recipe_data.get("output", ""),
            ingredients=recipe_data.get("ingredients", {}),
            required_profession=recipe_data.get("required_profession", ""),
            required_level=recipe_data.get("required_level", 1),
            xp_reward=recipe_data.get("xp_reward", 10),
        )
        
        db.add(recipe)
        count += 1
    
    db.commit()
    logger.info(f"✅ {count} recettes migrées")


def migrate_loot_tables(db):
    """Migre loot_tables.json → table loot_tables."""
    logger.info("🎲 Migration des loot tables...")
    
    data = load_json_file(config.LOOT_TABLES_FILE)
    count = 0
    
    for table_id, table_data in data.items():
        loot_table = LootTable(
            id=table_id,
            biomes=table_data.get("biomes", []),
            entries=table_data.get("table", []),
        )
        
        db.add(loot_table)
        count += 1
    
    db.commit()
    logger.info(f"✅ {count} loot tables migrées")


def migrate_quests(db):
    """Migre quests.json → table quests."""
    logger.info("🎯 Migration des quêtes...")
    
    data = load_json_file(config.QUESTS_FILE)
    count = 0
    
    for quest_id, quest_data in data.items():
        quest = Quest(
            id=quest_id,
            name=quest_data.get("name", ""),
            description=quest_data.get("description", ""),
            requirements=quest_data.get("requirements", {}),
            rewards=quest_data.get("reward", {}),
            required_level=quest_data.get("required_level", 1),
            required_profession=quest_data.get("required_profession"),
        )
        
        db.add(quest)
        count += 1
    
    db.commit()
    logger.info(f"✅ {count} quêtes migrées")


def migrate_settings(db):
    """Migre settings.json → table settings."""
    logger.info("⚙️  Migration des paramètres...")
    
    data = load_json_file(config.SETTINGS_FILE)
    count = 0
    
    for key, value in data.items():
        setting = Setting(
            key=key,
            value=value,
            description=f"Migrated from settings.json",
        )
        
        db.add(setting)
        count += 1
    
    db.commit()
    logger.info(f"✅ {count} paramètres migrés")


def main():
    """Point d'entrée principal."""
    logger.info("=" * 70)
    logger.info("🚀 MIGRATION JSON → PostgreSQL")
    logger.info("=" * 70)
    
    # 1. Initialise la DB (crée les tables)
    logger.info("🔧 Création des tables...")
    init_db()
    
    # 2. Ouvre une session
    db = SessionLocal()
    
    try:
        # 3. Migration par entité
        migrate_professions(db)
        migrate_resources(db)
        migrate_recipes(db)
        migrate_loot_tables(db)
        migrate_quests(db)
        migrate_users(db)
        migrate_refresh_tokens(db)
        migrate_settings(db)
        
        logger.info("=" * 70)
        logger.info("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ ERREUR DURANT LA MIGRATION: {e}", exc_info=True)
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()