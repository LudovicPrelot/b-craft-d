# app/utils/db_crud.py
"""
CRUD générique pour PostgreSQL avec SQLAlchemy.
Remplace utils/crud.py (JSON).
"""

from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from utils.logger import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """
    CRUD générique pour n'importe quel modèle SQLAlchemy.
    
    Usage:
        profession_crud = CRUDBase(Profession)
        profession = profession_crud.get(db, id="mineur")
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    # ========================================================================
    # READ
    # ========================================================================
    
    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """Récupère un élément par son ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_or_404(self, db: Session, id: str, name: str = "Item") -> ModelType:
        """Récupère ou lève HTTPException 404."""
        obj = self.get(db, id)
        if not obj:
            raise HTTPException(404, f"{name} '{id}' not found")
        return obj
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Liste avec pagination et filtres optionnels."""
        query = db.query(self.model)
        
        # Applique les filtres
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Compte le nombre total d'éléments."""
        query = db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    # ========================================================================
    # CREATE
    # ========================================================================
    
    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        """Crée un nouvel élément."""
        try:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"✅ Created {self.model.__name__} with id={obj_in.get('id')}")
            return db_obj
            
        except IntegrityError as e:
            db.rollback()
            logger.warning(f"⚠️  Integrity error creating {self.model.__name__}: {e}")
            
            # Détecte le type d'erreur
            if "unique" in str(e).lower():
                raise HTTPException(400, "Item with this ID already exists")
            raise HTTPException(400, f"Database constraint violation: {e}")
        
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating {self.model.__name__}", exc_info=True)
            raise HTTPException(500, f"Failed to create item: {e}")
    
    # ========================================================================
    # UPDATE
    # ========================================================================
    
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: ModelType, 
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Met à jour un élément existant."""
        try:
            for key, value in obj_in.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"✅ Updated {self.model.__name__} with id={db_obj.id}")
            return db_obj
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating {self.model.__name__}", exc_info=True)
            raise HTTPException(500, f"Failed to update item: {e}")
    
    def update_by_id(
        self, 
        db: Session, 
        *, 
        id: str, 
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Shortcut: récupère puis met à jour."""
        db_obj = self.get_or_404(db, id, self.model.__name__)
        return self.update(db, db_obj=db_obj, obj_in=obj_in)
    
    # ========================================================================
    # DELETE
    # ========================================================================
    
    def delete(self, db: Session, *, id: str) -> bool:
        """Supprime un élément."""
        try:
            obj = self.get_or_404(db, id, self.model.__name__)
            db.delete(obj)
            db.commit()
            
            logger.info(f"✅ Deleted {self.model.__name__} with id={id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error deleting {self.model.__name__}", exc_info=True)
            raise HTTPException(500, f"Failed to delete item: {e}")


# ============================================================================
# INSTANCES PRÊTES À L'EMPLOI
# ============================================================================

from models import User, Profession, Resource, Recipe, RefreshToken

user_crud = CRUDBase[User](User)
profession_crud = CRUDBase[Profession](Profession)
resource_crud = CRUDBase[Resource](Resource)
recipe_crud = CRUDBase[Recipe](Recipe)
refresh_token_crud = CRUDBase[RefreshToken](RefreshToken)


# ============================================================================
# HELPERS SPÉCIFIQUES
# ============================================================================

def get_user_by_login(db: Session, login: str) -> Optional[User]:
    """Récupère un utilisateur par son login."""
    return db.query(User).filter(User.login == login).first()


def get_user_by_mail(db: Session, mail: str) -> Optional[User]:
    """Récupère un utilisateur par son email."""
    return db.query(User).filter(User.mail == mail).first()


def get_recipes_by_profession(db: Session, profession: str) -> List[Recipe]:
    """Récupère les recettes pour une profession."""
    return db.query(Recipe).filter(Recipe.required_profession == profession).all()