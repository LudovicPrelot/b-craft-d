# app/routes/api/admin/users.py
"""
Routes Admin pour la gestion des utilisateurs - VERSION POSTGRESQL
"""

from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid

from utils.roles import require_admin
from utils.auth import hash_password
from utils.logger import get_logger
from utils.db_crud import user_crud
from database.connection import get_db
from models import User
from schemas.user import UserResponse, UserCreate
from services.xp_service import add_xp

logger = get_logger(__name__)

router = APIRouter(
    prefix="/users", 
    tags=["Admin - Users"], 
    dependencies=[Depends(require_admin)]
)


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Liste tous les utilisateurs."""
    logger.info(f"👥 Admin: Liste utilisateurs (skip={skip}, limit={limit})")
    
    try:
        users = user_crud.get_multi(db, skip=skip, limit=limit)
        logger.debug(f"   → {len(users)} utilisateur(s) trouvé(s)")
        return users
    except Exception as e:
        logger.error("❌ Erreur récupération utilisateurs", exc_info=True)
        raise HTTPException(500, "Failed to retrieve users")


@router.post("/create", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel utilisateur.
    
    Vérifie l'unicité du login et de l'email.
    """
    logger.info(f"➕ Admin: Création utilisateur (login: {payload.login})")
    
    # Vérification login unique
    existing = db.query(User).filter(User.login == payload.login).first()
    if existing:
        logger.warning(f"⚠️  Login {payload.login} déjà utilisé")
        raise HTTPException(400, "Login déjà utilisé")
    
    # Vérification email unique
    existing = db.query(User).filter(User.mail == payload.mail).first()
    if existing:
        logger.warning(f"⚠️  Mail {payload.mail} déjà utilisé")
        raise HTTPException(400, "Mail déjà utilisé")
    
    uid = str(uuid.uuid4())
    logger.debug(f"   → Génération ID: {uid}")
    
    try:
        user = User(
            id=uid,
            firstname=payload.firstname,
            lastname=payload.lastname,
            mail=payload.mail,
            login=payload.login,
            password_hash=hash_password(payload.password),
            profession=payload.profession or "",
            subclasses=[],
            inventory={},
            xp=0,
            level=1,
            stats={"strength": 1, "agility": 1, "endurance": 1},
            biome="",
            is_admin=False,
            is_moderator=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ Utilisateur {payload.login} créé (id: {uid})")
        return user
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur création utilisateur", exc_info=True)
        raise HTTPException(500, "Failed to create user")


@router.get("/{uid}", response_model=UserResponse)
def get_user(
    uid: str,
    db: Session = Depends(get_db)
):
    """Récupère un utilisateur par son ID."""
    logger.info(f"👤 Admin: Récupération utilisateur {uid}")
    
    user = user_crud.get_or_404(db, uid, "User")
    
    logger.debug(f"   → Utilisateur {uid} récupéré")
    return user


@router.put("/{uid}", response_model=UserResponse)
def update_user(
    uid: str,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Met à jour un utilisateur.
    
    Admin peut modifier:
    - firstname, lastname, mail
    - profession, subclasses
    - is_admin, is_moderator (privilèges)
    """
    logger.info(f"✏️  Admin: Mise à jour utilisateur {uid}")
    logger.debug(f"   → Champs: {list(payload.keys())}")
    
    try:
        user = user_crud.get_or_404(db, uid, "User")
        
        # Champs autorisés pour l'admin
        allowed = (
            "firstname", "lastname", "mail", 
            "profession", "subclasses", 
            "is_admin", "is_moderator"
        )
        
        for key in allowed:
            if key in payload:
                setattr(user, key, payload[key])
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ Utilisateur {uid} mis à jour")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur mise à jour utilisateur", exc_info=True)
        raise HTTPException(500, "Failed to update user")


@router.delete("/{uid}")
def delete_user(
    uid: str,
    db: Session = Depends(get_db)
):
    """
    Supprime un utilisateur.
    
    ⚠️ Supprime aussi ses refresh tokens.
    """
    logger.info(f"🗑️  Admin: Suppression utilisateur {uid}")
    
    try:
        # Supprime les refresh tokens associés
        from models import RefreshToken
        db.query(RefreshToken).filter(RefreshToken.user_id == uid).delete()
        
        # Supprime l'utilisateur
        user_crud.delete(db, id=uid)
        
        logger.info(f"✅ Utilisateur {uid} supprimé")
        return {"deleted": uid}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur suppression utilisateur", exc_info=True)
        raise HTTPException(500, "Failed to delete user")


@router.post("/{uid}/grant_xp")
def grant_xp(
    uid: str,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Accorde de l'XP à un utilisateur (admin only).
    
    Payload:
    - amount: Quantité d'XP à ajouter
    """
    amount = payload.get("amount", 0)
    
    if amount <= 0:
        logger.warning(f"⚠️  Montant invalide: {amount}")
        raise HTTPException(400, "amount must be > 0")
    
    logger.info(f"⭐ Admin: Ajout {amount} XP à utilisateur {uid}")
    
    try:
        user = user_crud.get_or_404(db, uid, "User")
        
        old_level = user.level
        add_xp(user, amount)
        
        db.commit()
        db.refresh(user)
        
        if user.level > old_level:
            logger.info(f"   🎉 Level up! {old_level} → {user.level}")
        else:
            logger.info(f"   ✅ {amount} XP ajoutée (Level: {user.level})")
        
        return {
            "status": "ok",
            "xp": user.xp,
            "level": user.level,
            "level_up": user.level > old_level
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur ajout XP", exc_info=True)
        raise HTTPException(500, "Failed to grant XP")