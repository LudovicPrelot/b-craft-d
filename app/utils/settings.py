from utils.json import load_json, save_json
import config

def get_settings():
    return load_json(config.SETTINGS_FILE)

def update_settings(new):
    save_json(config.SETTINGS_FILE, new)
