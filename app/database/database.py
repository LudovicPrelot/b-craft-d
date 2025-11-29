from utils.json import load_json, save_json
from models.resources import Resource
from models.recipes import Recipe
from models.professions import Profession
from config import RESOURCES_FILE, RECIPES_FILE, PROFESSIONS_FILE 

resources_json = load_json(RESOURCES_FILE)
recipes_json = load_json(RECIPES_FILE)
professions_json = load_json(PROFESSIONS_FILE)

resources_db = {rid: Resource(**data) for rid, data in resources_json.items()}
recipes_db = {rid: Recipe(**data) for rid, data in recipes_json.items()}
professions_db = {pid: Profession(**data) for pid, data in professions_json.items()}
