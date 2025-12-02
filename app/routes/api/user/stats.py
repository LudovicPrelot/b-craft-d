# app/routes/api/user/stats.py
"""
Routes user pour les stats et progression - VERSION POSTGRESQL
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from utils.roles import require_user
from utils.feature_flags import require_feature
from utils.logger import get_logger
from utils.db_crud import user_crud
from database.connection import get_db
from services.xp_service import add_xp, xp_for_level

logger = get_logger(__name__)

router = APIRouter(
    prefix="/stats", 
    tags=["Users - Stats"], 
    dependencies=[
        Depends(require_feature("enable_stats")),
        Depends(require_user)
    ]
)


@router.get("/")
def get_stats(
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les stats de progression de l'utilisateur.
    
    Returns:
    - xp: XP actuelle
    - level: Niveau actuel
    - stats: Statistiques (strength, agility, endurance)
    - next_level_xp: XP requise pour le prochain niveau
    - progress: Pourcentage de progression vers le prochain niveau
    """
    user_id = current.get("id")
    logger.info(f"📊 Stats pour user={user_id}")
    
    try:
        # Récupère l'utilisateur
        user = user_crud.get_or_404(db, user_id, "User")
        
        # Calcul XP prochain niveau
        next_level = xp_for_level(user.level + 1)
        
        # Calcul progression (%)
        progress = (user.xp / next_level * 100) if next_level > 0 else 0
        
        stats_data = {
            "xp": user.xp,
            "level": user.level,
            "stats": user.stats or {"strength": 1, "agility": 1, "endurance": 1},
            "next_level_xp": next_level,
            "progress_percent": round(progress, 1),
        }
        
        logger.debug(f"   → Level {user.level}, XP: {user.xp}/{next_level} ({progress:.1f}%)")
        
        return stats_data
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération stats: {e}", exc_info=True)
        raise HTTPException(500, "Failed to retrieve stats")


@router.post("/add_xp")
def add_xp_route(
    payload: dict = Body(...),
    current=Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Ajoute de l'XP à l'utilisateur.
    
    **Payload:**
    - amount: Quantité d'XP à ajouter (doit être > 0)
    
    **Process:**
    - Ajoute l'XP
    - Vérifie et applique level up si nécessaire
    - Augmente les stats si level up
    
    **Returns:**
    - xp: Nouvelle XP
    - level: Nouveau niveau
    - stats: Stats mises à jour
    - level_up: True si level up, False sinon
    - levels_gained: Nombre de niveaux gagnés (peut être > 1)
    """
    amount = payload.get("amount")
    
    if not amount or amount <= 0:
        logger.warning(f"⚠️  Montant XP invalide: {amount}")
        raise HTTPException(400, "amount must be > 0")
    
    user_id = current.get("id")
    logger.info(f"⭐ Ajout {amount} XP pour user={user_id}")
    
    try:
        # Récupère l'utilisateur
        user = user_crud.get_or_404(db, user_id, "User")
        
        # Sauvegarde état avant
        old_level = user.level
        old_xp = user.xp
        
        # Ajoute l'XP (gère automatiquement les level ups)
        add_xp(user, amount)
        
        # Commit en base
        db.commit()
        db.refresh(user)
        
        # Calcul progression
        levels_gained = user.level - old_level
        level_up = levels_gained > 0
        
        if level_up:
            logger.info(f"   🎉 Level up! {old_level} → {user.level} (+{levels_gained})")
        else:
            logger.info(f"   ✅ {amount} XP ajoutée (Level {user.level}, XP: {old_xp} → {user.xp})")
        
        return {
            "xp": user.xp,
            "level": user.level,
            "stats": user.stats,
            "level_up": level_up,
            "levels_gained": levels_gained,
            "xp_gained": amount,
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur ajout XP: {e}", exc_info=True)
        raise HTTPException(500, "Failed to add XP")