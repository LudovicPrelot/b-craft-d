# app/utils/logger.py
"""
Module de logging centralisé pour B-CraftD.

Usage dans tes autres fichiers :
    from utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Mon message")
    logger.error("Erreur détectée", exc_info=True)
"""

import logging
import sys
from datetime import datetime
import config


def setup_logging():
    """
    Configure le système de logging pour toute l'application.
    
    Crée deux handlers :
    - Console : affiche INFO+ (ou DEBUG si config.DEBUG=True)
    - Fichier : sauvegarde tout dans logs/app.log
    """
    
    # Utilise le dossier de logs défini dans config
    logs_dir = config.LOGS_DIR
    
    # Nom du fichier de log avec date
    log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configuration du niveau de log selon DEBUG
    log_level = logging.DEBUG if config.DEBUG else logging.INFO
    
    # Format détaillé pour les logs
    log_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Format simplifié pour la console
    console_format = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler pour la console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_format)
    
    # Handler pour le fichier (sauvegarde tout)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Sauvegarde tout dans le fichier
    file_handler.setFormatter(log_format)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Supprime les handlers existants pour éviter les doublons
    root_logger.handlers.clear()
    
    # Ajoute nos handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Réduit le bruit des librairies externes
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # Log de démarrage
    logger = logging.getLogger("b-craft-d")
    logger.info("=" * 70)
    logger.info("🚀 B-CraftD - Système de logging initialisé")
    logger.info(f"📊 Niveau de log : {'DEBUG' if config.DEBUG else 'INFO'}")
    logger.info(f"📁 Fichier de log : {log_file}")
    logger.info("=" * 70)


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger pour un module spécifique.
    
    Args:
        name: Nom du module (utilise __name__ généralement)
        
    Returns:
        Logger configuré pour ce module
        
    Example:
        logger = get_logger(__name__)
        logger.info("Message informatif")
        logger.debug("Détails de debug")
        logger.warning("Attention!")
        logger.error("Erreur!", exc_info=True)
    """
    return logging.getLogger(name)


# Initialise le logging au chargement du module
setup_logging()