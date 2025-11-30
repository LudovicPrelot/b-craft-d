# app/routes/api/__init__.py
from fastapi import APIRouter
from .admin import router as admin_router
from .moderator import router as moderator_router
from .public import router as public_router
from .user import router as user_router

router = APIRouter(prefix="/api")
router.include_router(admin_router)
router.include_router(moderator_router)
router.include_router(public_router)
router.include_router(user_router)
