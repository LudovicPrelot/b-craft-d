# app/utils/feature_flags.py
"""
Système de feature flags basé sur PostgreSQL.

Permet d'activer/désactiver des fonctionnalités de l'application
via des paramètres stockés en base de données.

Usage dans les routes:
    from utils.feature_flags import require_feature
    
    @router.get("/quests", dependencies=[Depends(require_feature("quests"))])
    def list_quests():
        # Cette route nécessite que la feature "quests" soit activée
        pass

Features disponibles:
- quests: Système de quêtes
- stats: Système de statistiques et progression
- crafting: Système de crafting (généralement toujours activé)
"""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from utils.settings import is_feature_enabled
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# FEATURE FLAGS DISPONIBLES
# ============================================================================

AVAILABLE_FEATURES = {
    "quests": {
        "name": "Quests",
        "description": "Système de quêtes et missions",
        "default": True,
    },
    "stats": {
        "name": "Stats",
        "description": "Système de statistiques et progression XP/Level",
        "default": True,
    },
    "crafting": {
        "name": "Crafting",
        "description": "Système de crafting d'items",
        "default": True,
    },
}


# ============================================================================
# DEPENDENCY POUR FASTAPI
# ============================================================================

def require_feature(feature_name: str):
    """
    Crée une dépendance FastAPI qui vérifie si une feature est activée.
    
    Lève une HTTPException 403 si la feature est désactivée.
    
    Args:
        feature_name: Nom de la feature (ex: "quests", "stats")
    
    Returns:
        Dependency callable pour FastAPI
    
    Usage:
        @router.get("/quests", dependencies=[Depends(require_feature("quests"))])
        def list_quests():
            # Cette route nécessite que la feature "quests" soit activée
            pass
    
    Raises:
        HTTPException 403: Si la feature est désactivée
    
    Example:
        # Dans une route
        @router.post(
            "/quests/{quest_id}/complete",
            dependencies=[Depends(require_feature("quests"))]
        )
        def complete_quest(quest_id: str, ...):
            # Code ici
            pass
        
        # Avec plusieurs features
        @router.post(
            "/crafting/craft",
            dependencies=[
                Depends(require_feature("crafting")),
                Depends(require_feature("stats"))  # Pour gain XP
            ]
        )
        def craft_item(...):
            pass
    """
    def _dependency(db: Session = Depends(get_db)):
        """Vérifie que la feature est activée."""
        
        # Vérifier si la feature existe
        if feature_name not in AVAILABLE_FEATURES:
            logger.warning(f"⚠️  Feature inconnue demandée: '{feature_name}'")
            # On laisse passer les features inconnues (fail-open)
            return
        
        # Vérifier si la feature est activée
        if not is_feature_enabled(db, feature_name):
            feature_info = AVAILABLE_FEATURES[feature_name]
            logger.info(f"🚫 Tentative d'accès à feature désactivée: '{feature_name}'")
            
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Feature disabled",
                    "feature": feature_name,
                    "message": f"La fonctionnalité '{feature_info['name']}' est actuellement désactivée."
                }
            )
        
        logger.debug(f"✅ Feature '{feature_name}' activée, accès autorisé")
    
    return _dependency


# ============================================================================
# HELPERS (pour utilisation hors routes)
# ============================================================================

def check_feature_enabled(db: Session, feature_name: str, raise_error: bool = True) -> bool:
    """
    Vérifie si une feature est activée (utilisation dans du code métier).
    
    Args:
        db: Session SQLAlchemy
        feature_name: Nom de la feature
        raise_error: Si True, lève une exception si désactivée
    
    Returns:
        True si activée, False sinon
    
    Raises:
        ValueError: Si raise_error=True et feature désactivée
    
    Example:
        # Dans un service
        def process_quest(db: Session, quest_id: str):
            if not check_feature_enabled(db, "quests", raise_error=False):
                logger.info("Quests désactivées, skip processing")
                return None
            
            # Code métier ici
    """
    if feature_name not in AVAILABLE_FEATURES:
        logger.warning(f"⚠️  Feature inconnue: '{feature_name}'")
        return True  # Fail-open pour features inconnues
    
    enabled = is_feature_enabled(db, feature_name)
    
    if not enabled and raise_error:
        feature_info = AVAILABLE_FEATURES[feature_name]
        raise ValueError(f"Feature '{feature_info['name']}' is disabled")
    
    return enabled


def get_all_features_status(db: Session) -> dict:
    """
    Récupère le statut de toutes les features disponibles.
    
    Args:
        db: Session SQLAlchemy
    
    Returns:
        Dict avec le statut de chaque feature
    
    Example:
        status = get_all_features_status(db)
        # {
        #     "quests": {
        #         "enabled": True,
        #         "name": "Quests",
        #         "description": "..."
        #     },
        #     ...
        # }
    """
    result = {}
    
    for feature_key, feature_info in AVAILABLE_FEATURES.items():
        enabled = is_feature_enabled(db, feature_key)
        
        result[feature_key] = {
            "enabled": enabled,
            "name": feature_info["name"],
            "description": feature_info["description"],
        }
    
    return result


# ============================================================================
# INITIALIZATION (pour main.py)
# ============================================================================

def init_feature_flags(db: Session, force_defaults: bool = False) -> None:
    """
    Initialise les feature flags au démarrage de l'application.
    
    Crée les settings pour chaque feature si ils n'existent pas.
    
    Args:
        db: Session SQLAlchemy
        force_defaults: Si True, reset toutes les features aux valeurs par défaut
    
    Example:
        # Dans main.py
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            db = SessionLocal()
            init_feature_flags(db)
            db.close()
            
            yield
    """
    from utils.settings import update_setting, setting_exists
    
    logger.info("🚩 Initialisation des feature flags...")
    
    created = 0
    updated = 0
    
    for feature_key, feature_info in AVAILABLE_FEATURES.items():
        setting_key = f"enable_{feature_key}"
        
        if setting_exists(db, setting_key) and not force_defaults:
            logger.debug(f"   → Feature '{feature_key}' existe déjà")
            continue
        
        # Créer ou mettre à jour
        update_setting(
            db,
            setting_key,
            feature_info["default"],
            description=f"Enable {feature_info['name']}: {feature_info['description']}",
            create_if_missing=True
        )
        
        if setting_exists(db, setting_key):
            if force_defaults:
                updated += 1
                logger.debug(f"   → Feature '{feature_key}' reset to default: {feature_info['default']}")
            else:
                created += 1
                logger.debug(f"   → Feature '{feature_key}' créée: {feature_info['default']}")
    
    logger.info(f"✅ Feature flags initialisés: {created} créé(s), {updated} reset")


# ============================================================================
# DECORATOR (pour utilisation dans les fonctions)
# ============================================================================

def requires_feature(feature_name: str):
    """
    Décorateur pour fonctions/méthodes qui nécessitent une feature.
    
    Note: La fonction doit accepter un paramètre 'db: Session'.
    
    Args:
        feature_name: Nom de la feature requise
    
    Example:
        @requires_feature("quests")
        def process_quest_completion(db: Session, quest_id: str):
            # Cette fonction nécessite la feature "quests"
            pass
        
        # Utilisation
        try:
            process_quest_completion(db, "quest_1")
        except ValueError as e:
            print(f"Feature disabled: {e}")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Trouver l'argument 'db' dans les kwargs ou args
            db = kwargs.get('db')
            if db is None:
                # Chercher dans args (assume que c'est le premier arg)
                if args and hasattr(args[0], 'query'):
                    db = args[0]
                else:
                    raise ValueError("Function must have a 'db' parameter (Session)")
            
            # Vérifier la feature
            check_feature_enabled(db, feature_name, raise_error=True)
            
            # Appeler la fonction
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# EXEMPLES D'UTILISATION
# ============================================================================

"""
EXEMPLE 1: Dans une route FastAPI
---------------------------------

from utils.feature_flags import require_feature

@router.get("/quests", dependencies=[Depends(require_feature("quests"))])
def list_quests(db: Session = Depends(get_db)):
    # Cette route est automatiquement bloquée si la feature est désactivée
    quests = db.query(Quest).all()
    return quests


EXEMPLE 2: Dans un service
--------------------------

from utils.feature_flags import check_feature_enabled

def award_quest_xp(db: Session, user_id: str, amount: int):
    # Vérifier si les quests et stats sont activés
    if not check_feature_enabled(db, "quests", raise_error=False):
        logger.info("Quests désactivées, skip XP award")
        return
    
    if not check_feature_enabled(db, "stats", raise_error=False):
        logger.info("Stats désactivées, skip XP award")
        return
    
    # Code métier ici
    user = db.query(User).get(user_id)
    add_xp(user, amount)


EXEMPLE 3: Vérification conditionnelle dans une route
-----------------------------------------------------

@router.post("/crafting/craft")
def craft_item(
    recipe_id: str,
    user = Depends(require_user),
    db: Session = Depends(get_db)
):
    # Craft l'item
    result = craft_recipe(db, user, recipe_id)
    
    # Si les stats sont activées, donner XP
    if check_feature_enabled(db, "stats", raise_error=False):
        add_xp(user, result.xp_reward)
    
    return result
"""