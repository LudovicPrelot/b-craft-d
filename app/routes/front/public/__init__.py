# app/routes/front/public/__init__.py
from fastapi import APIRouter
from .professions import router as professions_router

router = APIRouter(prefix="/public", include_in_schema=False)

router.include_router(professions_router)