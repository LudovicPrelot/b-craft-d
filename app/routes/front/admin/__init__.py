# app/routes/front/admin/__init__.py
from fastapi import APIRouter
from .professions import router as professions_router

router = APIRouter(prefix="/admin")

router.include_router(professions_router)
