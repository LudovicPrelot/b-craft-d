from utils.storage import load_json, save_json
import config

def get_settings():
    return load_json(config.BASE_DIR / "storage" / "settings.json")

def update_settings(new):
    save_json(config.BASE_DIR / "storage" / "settings.json", new)
