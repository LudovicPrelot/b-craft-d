from utils.json import load_json, save_json
from app.models.resource import Resource
from app.models.recipe import Recipe
from app.models.profession import Profession
from config import RESOURCES_FILE, RECIPES_FILE, PROFESSIONS_FILE 
from utils.logger import get_logger

# Initialise le logger
logger = get_logger(__name__)

logger.info("📚 Chargement des données depuis les fichiers JSON...")

# Chargement des données JSON
try:
    resources_json = load_json(RESOURCES_FILE)
    logger.debug(f"✅ {len(resources_json)} ressources chargées depuis {RESOURCES_FILE}")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement de {RESOURCES_FILE}", exc_info=True)
    raise

try:
    recipes_json = load_json(RECIPES_FILE)
    logger.debug(f"✅ {len(recipes_json)} recettes chargées depuis {RECIPES_FILE}")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement de {RECIPES_FILE}", exc_info=True)
    raise

try:
    professions_json = load_json(PROFESSIONS_FILE)
    logger.debug(f"✅ {len(professions_json)} professions chargées depuis {PROFESSIONS_FILE}")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement de {PROFESSIONS_FILE}", exc_info=True)
    raise

# Création des dictionnaires de données
logger.debug("🔄 Conversion des données JSON en objets Pydantic...")
resources_db = {rid: Resource(**data) for rid, data in resources_json.items()}
recipes_db = {rid: Recipe(**data) for rid, data in recipes_json.items()}
professions_db = {pid: Profession(**data) for pid, data in professions_json.items()}
logger.debug("✅ Conversion terminée")


def validate_data_integrity():
    """
    Vérifie l'intégrité des données au démarrage de l'application.
    Lance une ValueError si des incohérences sont détectées.
    
    Vérifications effectuées :
    - Toutes les professions requises dans les recettes existent
    - Tous les ingrédients des recettes correspondent à des ressources
    - Toutes les recettes autorisées dans les professions existent
    - Toutes les ressources trouvables dans les professions existent
    """
    logger.info("🔍 Démarrage de la validation d'intégrité des données...")
    errors = []
    warnings = []
    
    # 1. Vérifie que toutes les professions requises dans les recettes existent
    logger.debug("   → Vérification des professions requises dans les recettes")
    for recipe_id, recipe in recipes_db.items():
        prof = recipe.required_profession
        if prof not in professions_db:
            error_msg = f"Recipe '{recipe_id}' requires unknown profession '{prof}'"
            errors.append(error_msg)
            logger.error(f"   ❌ {error_msg}")
    
    # 2. Vérifie que tous les ingrédients des recettes existent comme ressources
    logger.debug("   → Vérification des ingrédients des recettes")
    for recipe_id, recipe in recipes_db.items():
        for ingredient in recipe.ingredients.keys():
            if ingredient not in resources_db:
                error_msg = f"Recipe '{recipe_id}' uses unknown resource '{ingredient}'"
                errors.append(error_msg)
                logger.error(f"   ❌ {error_msg}")
        
        # Vérifie aussi que l'output existe comme ressource
        if recipe.output not in resources_db:
            error_msg = f"Recipe '{recipe_id}' outputs unknown resource '{recipe.output}'"
            errors.append(error_msg)
            logger.error(f"   ❌ {error_msg}")
    
    # 3. Vérifie que toutes les recettes autorisées dans les professions existent
    logger.debug("   → Vérification des recettes autorisées par profession")
    for prof_id, prof in professions_db.items():
        for recipe_id in prof.allowed_recipes:
            if recipe_id not in recipes_db:
                error_msg = f"Profession '{prof_id}' allows unknown recipe '{recipe_id}'"
                errors.append(error_msg)
                logger.error(f"   ❌ {error_msg}")
    
    # 4. Vérifie que toutes les ressources trouvables existent
    logger.debug("   → Vérification des ressources trouvables par profession")
    for prof_id, prof in professions_db.items():
        for resource_id in prof.resources_found:
            if resource_id not in resources_db:
                error_msg = f"Profession '{prof_id}' can find unknown resource '{resource_id}'"
                errors.append(error_msg)
                logger.error(f"   ❌ {error_msg}")
    
    # 5. Vérifications bonus (warnings)
    logger.debug("   → Vérifications supplémentaires (warnings)")
    
    # Vérifie les professions sans ressources ni recettes
    for prof_id, prof in professions_db.items():
        if not prof.resources_found and not prof.allowed_recipes:
            warning_msg = f"Profession '{prof_id}' has no resources_found and no allowed_recipes"
            warnings.append(warning_msg)
            logger.warning(f"   ⚠️  {warning_msg}")
    
    # Affichage des résultats
    logger.info("=" * 70)
    if errors:
        logger.error(f"❌ {len(errors)} erreur(s) d'intégrité détectée(s)")
        for error in errors:
            logger.error(f"   • {error}")
        logger.error("=" * 70)
        raise ValueError(f"Data integrity check failed with {len(errors)} error(s)")
    
    if warnings:
        logger.warning(f"⚠️  {len(warnings)} avertissement(s) détecté(s)")
        for warning in warnings:
            logger.warning(f"   • {warning}")
    
    logger.info("✅ Vérification d'intégrité des données réussie!")
    logger.info(f"   📦 {len(resources_db)} ressources chargées")
    logger.info(f"   📜 {len(recipes_db)} recettes chargées")
    logger.info(f"   👷 {len(professions_db)} professions chargées")
    logger.info("=" * 70)


# Exécute la validation automatiquement au chargement du module
validate_data_integrity()