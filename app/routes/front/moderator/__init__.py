# app/routes/front/moderator/__init__.py
from fastapi import APIRouter
from .professions import router as professions_router

router = APIRouter(prefix="/moderator")

router.include_router(professions_router)
