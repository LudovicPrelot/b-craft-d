# app/routes/front/user/__init__.py
from fastapi import APIRouter
from .professions import router as professions_router

router = APIRouter(prefix="/user")

router.include_router(professions_router)
