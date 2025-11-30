# app/routes/api/public/__init__.py
from fastapi import APIRouter
from .auth import router as auth_router
from .professions import router as professions_router
from .quests import router as quests_router
from .recipes import router as recipes_router
from .resources import router as resources_router

router = APIRouter(prefix="/public")

router.include_router(auth_router)
router.include_router(professions_router)
router.include_router(quests_router)
router.include_router(recipes_router)
router.include_router(resources_router)
