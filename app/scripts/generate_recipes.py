import json
from pathlib import Path

STORAGE = Path("storage")

def load_json(filename: str):
    path = STORAGE / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename: str, content: dict):
    path = STORAGE / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4, ensure_ascii=False)

def main():
    # Chargement des données existantes
    resources = load_json("resources.json")
    professions = load_json("professions.json")
    recipes = load_json("recipes.json")

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

    save_json("recipes.json", recipes)
    print("✔ recipes.json mis à jour en utilisant les fichiers /storage")

if __name__ == "__main__":
    main()
