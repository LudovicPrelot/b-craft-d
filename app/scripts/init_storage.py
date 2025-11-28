# scripts/init_storage.py
from pathlib import Path
import json
import config

def ensure_file(path, default):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(default, indent=4, ensure_ascii=False), encoding='utf-8')

def main():
    ensure_file(config.USERS_FILE, {})
    ensure_file(config.PROFESSIONS_FILE, {
        "mineur": {
            "id":"mineur","name":"Mineur",
            "resources_found":["argile","calcaire"],
            "allowed_recipes":["ciment"],
            "subclasses":["foreur","géologue"]
        }
    })
    ensure_file(config.RECIPES_FILE, {})
    ensure_file(config.REFRESH_TOKENS_FILE, {})
    ensure_file(config.FAILED_LOGINS_FILE, {})
    print("Storage initialisé.")

if __name__ == "__main__":
    main()
