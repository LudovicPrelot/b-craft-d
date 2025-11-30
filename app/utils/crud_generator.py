# app/utils/crud.py
"""
Fonctions CRUD réutilisables pour gérer les ressources JSON.

Usage dans les routes :
    from utils.crud import list_all, get_one, create_one, update_one, delete_one
    
    @router.get("/")
    def list_professions():
        return list_all(config.PROFESSIONS_FILE, "professions", logger)
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from utils.json import load_json, save_json
import logging

# ============================================================================
# READ Operations
# ============================================================================

def list_all(
    file_path: Path,
    resource_name: str,
    logger: logging.Logger,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Liste tous les éléments d'une ressource.
    
    Args:
        file_path: Chemin du fichier JSON
        resource_name: Nom de la ressource (pour les logs)
        logger: Logger à utiliser
        user_id: ID de l'utilisateur (optionnel, pour les logs)
    
    Returns:
        Liste des éléments
    
    Raises:
        HTTPException: 500 si erreur de lecture
    
    Example:
        items = list_all(config.PROFESSIONS_FILE, "professions", logger)
    """
    log_prefix = f"user_id={user_id}" if user_id else "public"
    logger.info(f"📋 Liste des {resource_name} ({log_prefix})")
    
    try:
        data = load_json(file_path) or {}
        items = list(data.values())
        logger.debug(f"   → {len(items)} {resource_name} trouvé(s)")
        return items
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des {resource_name}", exc_info=True)
        raise HTTPException(500, f"Failed to retrieve {resource_name}")


def get_one(
    file_path: Path,
    item_id: str,
    resource_name: str,
    logger: logging.Logger,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Récupère un élément par son ID.
    
    Args:
        file_path: Chemin du fichier JSON
        item_id: ID de l'élément à récupérer
        resource_name: Nom de la ressource (pour les logs)
        logger: Logger à utiliser
        user_id: ID de l'utilisateur (optionnel, pour les logs)
    
    Returns:
        Élément trouvé
    
    Raises:
        HTTPException: 404 si non trouvé, 500 si erreur
    
    Example:
        profession = get_one(config.PROFESSIONS_FILE, "mineur", "profession", logger)
    """
    log_prefix = f"user_id={user_id}" if user_id else "public"
    logger.info(f"🔍 Récupération {resource_name} '{item_id}' ({log_prefix})")
    
    try:
        data = load_json(file_path) or {}
        
        if item_id not in data:
            logger.warning(f"⚠️  {resource_name.capitalize()} '{item_id}' non trouvé")
            raise HTTPException(404, f"{resource_name.capitalize()} not found")
        
        item = data[item_id]
        logger.debug(f"   → {resource_name.capitalize()} '{item_id}' récupéré")
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du {resource_name}", exc_info=True)
        raise HTTPException(500, f"Failed to retrieve {resource_name}")


# ============================================================================
# CREATE Operation
# ============================================================================

def create_one(
    file_path: Path,
    payload: Dict[str, Any],
    resource_name: str,
    logger: logging.Logger,
    id_field: str = "id"
) -> Dict[str, Any]:
    """
    Crée un nouvel élément.
    
    Args:
        file_path: Chemin du fichier JSON
        payload: Données de l'élément à créer
        resource_name: Nom de la ressource (pour les logs)
        logger: Logger à utiliser
        id_field: Nom du champ ID (par défaut "id")
    
    Returns:
        Élément créé
    
    Raises:
        HTTPException: 400 si ID manquant ou existe déjà, 500 si erreur
    
    Example:
        profession = create_one(
            config.PROFESSIONS_FILE,
            {"id": "mineur", "name": "Mineur"},
            "profession",
            logger
        )
    """
    item_id = payload.get(id_field)
    
    if not item_id:
        logger.warning(f"⚠️  Tentative de création sans {id_field}")
        raise HTTPException(400, f"{id_field} is required")
    
    logger.info(f"➕ Création {resource_name} '{item_id}'")
    
    try:
        data = load_json(file_path) or {}
        
        if item_id in data:
            logger.warning(f"⚠️  {resource_name.capitalize()} '{item_id}' existe déjà")
            raise HTTPException(400, f"{resource_name.capitalize()} already exists")
        
        data[item_id] = payload
        save_json(file_path, data)
        
        logger.info(f"✅ {resource_name.capitalize()} '{item_id}' créé avec succès")
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création du {resource_name}", exc_info=True)
        raise HTTPException(500, f"Failed to create {resource_name}")


# ============================================================================
# UPDATE Operation
# ============================================================================

def update_one(
    file_path: Path,
    item_id: str,
    payload: Dict[str, Any],
    resource_name: str,
    logger: logging.Logger,
    merge: bool = True
) -> Dict[str, Any]:
    """
    Met à jour un élément existant.
    
    Args:
        file_path: Chemin du fichier JSON
        item_id: ID de l'élément à mettre à jour
        payload: Nouvelles données
        resource_name: Nom de la ressource (pour les logs)
        logger: Logger à utiliser
        merge: Si True, fusionne avec l'existant. Si False, remplace complètement.
    
    Returns:
        Élément mis à jour
    
    Raises:
        HTTPException: 404 si non trouvé, 500 si erreur
    
    Example:
        updated = update_one(
            config.PROFESSIONS_FILE,
            "mineur",
            {"name": "Grand Mineur"},
            "profession",
            logger
        )
    """
    logger.info(f"✏️  Mise à jour {resource_name} '{item_id}'")
    logger.debug(f"   → Champs: {list(payload.keys())}")
    
    try:
        data = load_json(file_path) or {}
        
        if item_id not in data:
            logger.warning(f"⚠️  {resource_name.capitalize()} '{item_id}' non trouvé")
            raise HTTPException(404, f"{resource_name.capitalize()} not found")
        
        if merge:
            # Fusion avec l'existant
            data[item_id].update(payload)
        else:
            # Remplacement complet
            data[item_id] = payload
        
        save_json(file_path, data)
        
        logger.info(f"✅ {resource_name.capitalize()} '{item_id}' mis à jour")
        return data[item_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour du {resource_name}", exc_info=True)
        raise HTTPException(500, f"Failed to update {resource_name}")


# ============================================================================
# DELETE Operation
# ============================================================================

def delete_one(
    file_path: Path,
    item_id: str,
    resource_name: str,
    logger: logging.Logger
) -> Dict[str, Any]:
    """
    Supprime un élément.
    
    Args:
        file_path: Chemin du fichier JSON
        item_id: ID de l'élément à supprimer
        resource_name: Nom de la ressource (pour les logs)
        logger: Logger à utiliser
    
    Returns:
        Dict avec status et id de l'élément supprimé
    
    Raises:
        HTTPException: 404 si non trouvé, 500 si erreur
    
    Example:
        result = delete_one(config.PROFESSIONS_FILE, "mineur", "profession", logger)
    """
    logger.info(f"🗑️  Suppression {resource_name} '{item_id}'")
    
    try:
        data = load_json(file_path) or {}
        
        if item_id not in data:
            logger.warning(f"⚠️  {resource_name.capitalize()} '{item_id}' non trouvé")
            raise HTTPException(404, f"{resource_name.capitalize()} not found")
        
        del data[item_id]
        save_json(file_path, data)
        
        logger.info(f"✅ {resource_name.capitalize()} '{item_id}' supprimé")
        return {"status": "deleted", "id": item_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression du {resource_name}", exc_info=True)
        raise HTTPException(500, f"Failed to delete {resource_name}")


# ============================================================================
# BULK Operations (bonus)
# ============================================================================

def bulk_create(
    file_path: Path,
    items: List[Dict[str, Any]],
    resource_name: str,
    logger: logging.Logger,
    id_field: str = "id",
    skip_existing: bool = False
) -> Dict[str, Any]:
    """
    Crée plusieurs éléments en une seule opération.
    
    Args:
        file_path: Chemin du fichier JSON
        items: Liste des éléments à créer
        resource_name: Nom de la ressource (pour les logs)
        logger: Logger à utiliser
        id_field: Nom du champ ID
        skip_existing: Si True, ignore les doublons. Si False, erreur sur doublon.
    
    Returns:
        Dict avec le nombre créé/ignoré/erreurs
    
    Example:
        result = bulk_create(
            config.PROFESSIONS_FILE,
            [{"id": "mineur", ...}, {"id": "bucheron", ...}],
            "professions",
            logger
        )
    """
    logger.info(f"➕ Création en masse de {len(items)} {resource_name}")
    
    try:
        data = load_json(file_path) or {}
        
        created = 0
        skipped = 0
        errors = []
        
        for item in items:
            item_id = item.get(id_field)
            
            if not item_id:
                errors.append(f"Missing {id_field}")
                continue
            
            if item_id in data:
                if skip_existing:
                    logger.debug(f"   → {item_id} existe déjà, ignoré")
                    skipped += 1
                    continue
                else:
                    errors.append(f"{item_id} already exists")
                    continue
            
            data[item_id] = item
            created += 1
            logger.debug(f"   → {item_id} créé")
        
        if created > 0:
            save_json(file_path, data)
        
        logger.info(f"✅ Création en masse terminée: {created} créés, {skipped} ignorés, {len(errors)} erreurs")
        
        return {
            "created": created,
            "skipped": skipped,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création en masse", exc_info=True)
        raise HTTPException(500, f"Failed to bulk create {resource_name}")