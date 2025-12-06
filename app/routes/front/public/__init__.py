# app/routes/front/public/__init__.py
from fastapi import APIRouter
from .professions import router as professions_router
from .recipes import router as recipes_router
from .resources import router as resources_router

router = APIRouter(prefix="/public", include_in_schema=False)

router.include_router(professions_router)
router.include_router(recipes_router)
router.include_router(resources_router)