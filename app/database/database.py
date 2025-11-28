from utils.json_loader import load_json
from models.resources import Resource
from models.recipes import Recipe
from models.professions import Profession

resources_json = load_json("storage/resources.json")
recipes_json = load_json("storage/recipes.json")
professions_json = load_json("storage/professions.json")

resources_db = {rid: Resource(**data) for rid, data in resources_json.items()}
recipes_db = {rid: Recipe(**data) for rid, data in recipes_json.items()}
professions_db = {pid: Profession(**data) for pid, data in professions_json.items()}
