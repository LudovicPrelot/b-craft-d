import os
from pathlib import Path

# Racine du projet
BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# ENVIRONMENT VARIABLES (lecture simple) — valeurs par défaut en dev
# ---------------------------------------------------------------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET_IN_PRODUCTION")
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
USERS_FILE = STORAGE_DIR / "users.json"
PROFESSIONS_FILE = STORAGE_DIR / "professions.json"
RECIPES_FILE = STORAGE_DIR / "recipes.json"
RESOURCES_FILE = STORAGE_DIR / "resources.json"
REFRESH_TOKENS_FILE = STORAGE_DIR / "refresh_tokens.json"
FAILED_LOGINS_FILE = STORAGE_DIR / "failed_logins.json"

TEMPLATES_DIR = WEB_INTERFACE_DIR / "templates"
STATIC_DIR = WEB_INTERFACE_DIR / "static"

# Make sure dirs exist in dev
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
WEB_INTERFACE_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
