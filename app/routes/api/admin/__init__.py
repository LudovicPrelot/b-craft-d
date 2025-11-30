# app/routes/api/admin/__init__.py

from fastapi import APIRouter
from .loot import router as loot_router
from .professions import router as professions_router
from .recipes import router as recipes_router
from .resources import router as resources_router
from .settings import router as settings_router
from .users import router as users_router

router = APIRouter(prefix="/admin")

router.include_router(loot_router)
router.include_router(professions_router)
router.include_router(resources_router)
router.include_router(recipes_router)
router.include_router(resources_router)
router.include_router(settings_router)
router.include_router(users_router)
