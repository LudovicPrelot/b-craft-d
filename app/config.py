import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

import secrets
from pathlib import Path

# Racine du projet
BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# ENVIRONMENT VARIABLES (lecture simple) – valeurs par défaut en dev
# ---------------------------------------------------------------------------

# JWT Secret avec génération automatique sécurisée
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    JWT_SECRET_KEY = secrets.token_urlsafe(32)
    print("⚠️  WARNING: Using auto-generated JWT secret.")
    print("   Set JWT_SECRET_KEY environment variable in production!")
    print(f"   Generated secret: {JWT_SECRET_KEY}")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 14))

BF_THRESHOLD = int(os.getenv("BF_THRESHOLD", 5))
BF_WINDOW_SECONDS = int(os.getenv("BF_WINDOW_SECONDS", 900))      # 15 min
BF_BLOCK_SECONDS = int(os.getenv("BF_BLOCK_SECONDS", 900))        # 15 min

DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# ---------------------------------------------------------------------------
# STORAGE FILES & DIRECTORIES
# ---------------------------------------------------------------------------
STORAGE_DIR = BASE_DIR / "storage"
WEB_INTERFACE_DIR = BASE_DIR / "web_interface"
LOGS_DIR = BASE_DIR / "logs"

TEMPLATES_DIR = WEB_INTERFACE_DIR / "templates"
STATIC_DIR = WEB_INTERFACE_DIR / "static"

ADMIN_TEMPLATES_DIR = TEMPLATES_DIR / "admin"
MODERATOR_TEMPLATES_DIR = TEMPLATES_DIR / "moderator"
USER_TEMPLATES_DIR = TEMPLATES_DIR / "user"
PUBLIC_TEMPLATES_DIR = TEMPLATES_DIR / "public"

FAILED_LOGINS_FILE = STORAGE_DIR / "failed_logins.json"
LOOT_ENVIRONMENT_FILE = STORAGE_DIR / "loot_environment.json"
LOOT_TABLES_FILE = STORAGE_DIR / "loot_tables.json"
PROFESSIONS_FILE = STORAGE_DIR / "professions.json"
QUESTS_FILE = STORAGE_DIR / "quests.json"
RECIPES_FILE = STORAGE_DIR / "recipes.json"
REFRESH_TOKENS_FILE = STORAGE_DIR / "refresh_tokens.json"
RESOURCES_FILE = STORAGE_DIR / "resources.json"
SETTINGS_FILE = STORAGE_DIR / "settings.json"
USERS_FILE = STORAGE_DIR / "users.json"

# Make sure dirs exist in dev
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
WEB_INTERFACE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

ADMIN_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
MODERATOR_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
USER_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)