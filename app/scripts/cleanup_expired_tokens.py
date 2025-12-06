#!/usr/bin/env python3
# app/scripts/cleanup_expired_tokens.py
"""
Script de nettoyage des refresh tokens expirés.

Usage:
    python -m scripts.cleanup_expired_tokens
    
Recommandation: Exécuter via cron toutes les heures
    0 * * * * cd /app && python -m scripts.cleanup_expired_tokens
"""

import sys
from pathlib import Path

# Ajoute app/ au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_db_context
from utils.auth import cleanup_expired_tokens
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Point d'entrée principal."""
    logger.info("=" * 70)
    logger.info("🧹 NETTOYAGE DES REFRESH TOKENS EXPIRÉS")
    logger.info("=" * 70)
    
    try:
        with get_db_context() as db:
            deleted = cleanup_expired_tokens(db)
            
            if deleted > 0:
                logger.info(f"✅ {deleted} token(s) expiré(s) supprimé(s)")
            else:
                logger.info("✅ Aucun token expiré trouvé")
        
        logger.info("=" * 70)
        logger.info("✅ NETTOYAGE TERMINÉ")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ ERREUR DURANT LE NETTOYAGE: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()