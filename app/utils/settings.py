# app/utils/settings.py
"""
Service de gestion des paramètres (feature flags) - VERSION POSTGRESQL

Remplace le système de stockage JSON par PostgreSQL.
Les settings sont stockés dans la table 'settings' avec structure:
- key (str) - Clé unique du paramètre
- value (JSON) - Valeur (peut être bool, int, str, dict, list)
- description (str) - Description du paramètre
- updated_at (datetime) - Date de dernière mise à jour

Usage:
    from utils.settings import get_setting, update_setting, get_all_settings
    
    # Récupérer un setting
    enable_loot = get_setting(db, "enable_loot", default=False)
    
    # Mettre à jour
    update_setting(db, "enable_loot", True)
    
    # Récupérer tous les settings
    all_settings = get_all_settings(db)
"""

from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
from datetime import datetime

from models import Setting
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# GET SETTINGS
# ============================================================================

def get_setting(
    db: Session, 
    key: str, 
    default: Any = None
) -> Any:
    """
    Récupère la valeur d'un paramètre.
    
    Args:
        db: Session SQLAlchemy
        key: Clé du paramètre (ex: "enable_loot")
        default: Valeur par défaut si le paramètre n'existe pas
    
    Returns:
        La valeur du paramètre ou la valeur par défaut
    
    Example:
        enable_loot = get_setting(db, "enable_loot", default=False)
        if enable_loot:
            # Feature loot activée
    """
    logger.debug(f"⚙️  Récupération setting '{key}'")
    
    setting = db.query(Setting).filter(Setting.key == key).first()
    
    if setting is None:
        logger.debug(f"   → Setting '{key}' non trouvé, utilisation default: {default}")
        return default
    
    logger.debug(f"   → Setting '{key}' = {setting.value}")
    return setting.value


def get_all_settings(db: Session) -> Dict[str, Any]:
    """
    Récupère tous les paramètres.
    
    Args:
        db: Session SQLAlchemy
    
    Returns:
        Dict {key: value} de tous les paramètres
    
    Example:
        settings = get_all_settings(db)
        # {'enable_loot': True, 'enable_stats': True, ...}
    """
    logger.debug("⚙️  Récupération de tous les settings")
    
    settings = db.query(Setting).all()
    
    result = {s.key: s.value for s in settings}
    
    logger.debug(f"   → {len(result)} setting(s) récupéré(s)")
    return result


def setting_exists(db: Session, key: str) -> bool:
    """
    Vérifie si un paramètre existe.
    
    Args:
        db: Session SQLAlchemy
        key: Clé du paramètre
    
    Returns:
        True si le paramètre existe, False sinon
    
    Example:
        if setting_exists(db, "enable_loot"):
            # Le setting existe
    """
    return db.query(Setting).filter(Setting.key == key).first() is not None


# ============================================================================
# UPDATE SETTINGS
# ============================================================================

def update_setting(
    db: Session,
    key: str,
    value: Any,
    description: Optional[str] = None,
    create_if_missing: bool = True
) -> Setting:
    """
    Met à jour un paramètre (ou le crée s'il n'existe pas).
    
    Args:
        db: Session SQLAlchemy
        key: Clé du paramètre
        value: Nouvelle valeur (bool, int, str, dict, list)
        description: Description optionnelle (si création)
        create_if_missing: Si True, crée le setting s'il n'existe pas
    
    Returns:
        L'objet Setting mis à jour
    
    Raises:
        ValueError: Si le setting n'existe pas et create_if_missing=False
    
    Example:
        # Activer le loot
        update_setting(db, "enable_loot", True)
        
        # Désactiver les stats
        update_setting(db, "enable_stats", False)
        
        # Mettre à jour avec description
        update_setting(
            db, 
            "max_inventory_slots", 
            100, 
            description="Nombre max de slots d'inventaire"
        )
    """
    logger.info(f"💾 Mise à jour setting '{key}' = {value}")
    
    # Cherche le setting existant
    setting = db.query(Setting).filter(Setting.key == key).first()
    
    if setting:
        # Mise à jour
        logger.debug(f"   → Mise à jour existant (ancienne valeur: {setting.value})")
        setting.value = value
        if description:
            setting.description = description
        setting.updated_at = datetime.now()
        
    else:
        # Création
        if not create_if_missing:
            logger.error(f"❌ Setting '{key}' non trouvé et create_if_missing=False")
            raise ValueError(f"Setting '{key}' does not exist")
        
        logger.debug(f"   → Création nouveau setting")
        setting = Setting(
            key=key,
            value=value,
            description=description or f"Setting {key}",
        )
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    
    logger.info(f"✅ Setting '{key}' sauvegardé")
    return setting


def update_settings_bulk(
    db: Session,
    settings_dict: Dict[str, Any],
    create_if_missing: bool = True
) -> Dict[str, Any]:
    """
    Met à jour plusieurs paramètres en une seule transaction.
    
    Args:
        db: Session SQLAlchemy
        settings_dict: Dict {key: value} des paramètres à mettre à jour
        create_if_missing: Si True, crée les settings manquants
    
    Returns:
        Dict {key: value} des paramètres mis à jour
    
    Example:
        update_settings_bulk(db, {
            "enable_loot": True,
            "enable_stats": True,
            "enable_quests": False
        })
    """
    logger.info(f"💾 Mise à jour bulk de {len(settings_dict)} setting(s)")
    
    result = {}
    
    for key, value in settings_dict.items():
        setting = update_setting(db, key, value, create_if_missing=create_if_missing)
        result[key] = setting.value
    
    logger.info(f"✅ {len(result)} setting(s) mis à jour")
    return result


# ============================================================================
# DELETE SETTINGS
# ============================================================================

def delete_setting(db: Session, key: str) -> bool:
    """
    Supprime un paramètre.
    
    Args:
        db: Session SQLAlchemy
        key: Clé du paramètre à supprimer
    
    Returns:
        True si supprimé, False si n'existait pas
    
    Example:
        deleted = delete_setting(db, "old_setting")
    """
    logger.info(f"🗑️  Suppression setting '{key}'")
    
    deleted = db.query(Setting).filter(Setting.key == key).delete()
    db.commit()
    
    if deleted:
        logger.info(f"✅ Setting '{key}' supprimé")
        return True
    else:
        logger.warning(f"⚠️  Setting '{key}' non trouvé")
        return False


# ============================================================================
# FEATURE FLAGS (Helpers spécifiques)
# ============================================================================

def is_feature_enabled(db: Session, feature_name: str) -> bool:
    """
    Vérifie si une feature est activée.
    
    Convention: Les features flags sont préfixés par "enable_"
    
    Args:
        db: Session SQLAlchemy
        feature_name: Nom de la feature (ex: "loot", "stats")
    
    Returns:
        True si la feature est activée, False sinon
    
    Example:
        if is_feature_enabled(db, "loot"):
            # Feature loot activée
            return collect_loot(user)
    """
    key = f"enable_{feature_name}" if not feature_name.startswith("enable_") else feature_name
    return get_setting(db, key, default=False)


def enable_feature(db: Session, feature_name: str) -> None:
    """
    Active une feature.
    
    Args:
        db: Session SQLAlchemy
        feature_name: Nom de la feature
    
    Example:
        enable_feature(db, "loot")
    """
    key = f"enable_{feature_name}" if not feature_name.startswith("enable_") else feature_name
    update_setting(db, key, True, description=f"Enable {feature_name} feature")
    logger.info(f"✅ Feature '{feature_name}' activée")


def disable_feature(db: Session, feature_name: str) -> None:
    """
    Désactive une feature.
    
    Args:
        db: Session SQLAlchemy
        feature_name: Nom de la feature
    
    Example:
        disable_feature(db, "loot")
    """
    key = f"enable_{feature_name}" if not feature_name.startswith("enable_") else feature_name
    update_setting(db, key, False, description=f"Enable {feature_name} feature")
    logger.info(f"⚠️  Feature '{feature_name}' désactivée")


def toggle_feature(db: Session, feature_name: str) -> bool:
    """
    Inverse l'état d'une feature (ON → OFF ou OFF → ON).
    
    Args:
        db: Session SQLAlchemy
        feature_name: Nom de la feature
    
    Returns:
        Le nouvel état (True = activée, False = désactivée)
    
    Example:
        new_state = toggle_feature(db, "loot")
        print(f"Loot is now {'enabled' if new_state else 'disabled'}")
    """
    current = is_feature_enabled(db, feature_name)
    new_state = not current
    
    key = f"enable_{feature_name}" if not feature_name.startswith("enable_") else feature_name
    update_setting(db, key, new_state)
    
    logger.info(f"🔄 Feature '{feature_name}' toggled: {current} → {new_state}")
    return new_state


# ============================================================================
# INITIALIZATION (pour démarrage application)
# ============================================================================

DEFAULT_SETTINGS = {
    "enable_loot": True,
    "enable_stats": True,
    "enable_quests": True,
    "enable_crafting": True,
    "max_inventory_slots": 100,
    "max_level": 100,
    "base_xp": 100,
    "xp_multiplier": 1.5,
}


def init_default_settings(db: Session, force_update: bool = False) -> None:
    """
    Initialise les paramètres par défaut au démarrage de l'application.
    
    Args:
        db: Session SQLAlchemy
        force_update: Si True, écrase les valeurs existantes
    
    Example:
        # Dans main.py au démarrage
        from database.connection import SessionLocal
        from utils.settings import init_default_settings
        
        db = SessionLocal()
        init_default_settings(db)
        db.close()
    """
    logger.info("🔧 Initialisation des settings par défaut...")
    
    created = 0
    updated = 0
    
    for key, value in DEFAULT_SETTINGS.items():
        existing = db.query(Setting).filter(Setting.key == key).first()
        
        if existing and not force_update:
            logger.debug(f"   → Setting '{key}' existe déjà, skip")
            continue
        
        if existing and force_update:
            existing.value = value
            existing.updated_at = datetime.now()
            updated += 1
            logger.debug(f"   → Setting '{key}' mis à jour (force)")
        else:
            new_setting = Setting(
                key=key,
                value=value,
                description=f"Default setting for {key}",
            )
            db.add(new_setting)
            created += 1
            logger.debug(f"   → Setting '{key}' créé")
    
    db.commit()
    
    logger.info(f"✅ Settings initialisés: {created} créé(s), {updated} mis à jour")


# ============================================================================
# EXPORT / IMPORT (pour backup/restore)
# ============================================================================

def export_settings_to_dict(db: Session) -> Dict[str, Dict[str, Any]]:
    """
    Exporte tous les settings dans un dict (pour backup).
    
    Returns:
        Dict avec structure complète (key, value, description, updated_at)
    
    Example:
        settings = export_settings_to_dict(db)
        json.dump(settings, open("settings_backup.json", "w"))
    """
    logger.info("📤 Export des settings...")
    
    settings = db.query(Setting).all()
    
    result = {
        s.key: {
            "value": s.value,
            "description": s.description,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        }
        for s in settings
    }
    
    logger.info(f"✅ {len(result)} setting(s) exporté(s)")
    return result


def import_settings_from_dict(
    db: Session, 
    settings_dict: Dict[str, Dict[str, Any]],
    overwrite: bool = False
) -> None:
    """
    Importe des settings depuis un dict (pour restore).
    
    Args:
        db: Session SQLAlchemy
        settings_dict: Dict exporté par export_settings_to_dict()
        overwrite: Si True, écrase les valeurs existantes
    
    Example:
        settings = json.load(open("settings_backup.json"))
        import_settings_from_dict(db, settings, overwrite=True)
    """
    logger.info(f"📥 Import de {len(settings_dict)} setting(s)...")
    
    for key, data in settings_dict.items():
        if isinstance(data, dict):
            value = data.get("value")
            description = data.get("description")
        else:
            # Format simplifié {key: value}
            value = data
            description = None
        
        existing = db.query(Setting).filter(Setting.key == key).first()
        
        if existing and not overwrite:
            logger.debug(f"   → Setting '{key}' existe, skip (overwrite=False)")
            continue
        
        update_setting(db, key, value, description=description, create_if_missing=True)
    
    logger.info(f"✅ Settings importés")