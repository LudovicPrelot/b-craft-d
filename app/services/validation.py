from database.database import resources_db, recipes_db, professions_db

def validate_recipe(recipe_id: str):
    if recipe_id not in recipes_db:
        return False, "Recette introuvable"

    r = recipes_db[recipe_id]

    # Vérifier ressources ingrédients
    for ing in r.ingredients:
        if ing not in resources_db:
            return False, f"Ressource inconnue: {ing}"

    # Vérifier ressource output
    if r.output not in resources_db:
        return False, "Ressource output inconnue"

    # Vérifier profession
    if r.required_profession not in professions_db:
        return False, "Métier inconnu"

    return True, "OK"
