import json
from pathlib import Path
from utils.json import load_json, save_json
from config import RESOURCES_FILE, PROFESSIONS_FILE, RECIPES_FILE

def main():
    # Chargement des données existantes
    resources = load_json(RESOURCES_FILE)
    professions = load_json(PROFESSIONS_FILE)
    recipes = load_json(RECIPES_FILE)

    # Exemple : auto-génération d'une recette simple par métier
    # (si une ressource est trouvable par un métier, il peut la transformer)
    for prof_id, data in professions.items():
        for res in data.get("resources_found", []):
            # On ne génère une recette que si elle n'existe pas déjà
            auto_recipe_id = f"{prof_id}_transform_{res}"
            if auto_recipe_id not in recipes:
                recipes[auto_recipe_id] = {
                    "output": res,
                    "ingredients": {res: 1},
                    "required_profession": prof_id
                }

    save_json(RECIPES_FILE, recipes)
    print("✔ recipes.json mis à jour en utilisant les fichiers /storage")

if __name__ == "__main__":
    main()
