# app/routes/front/__init__.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from utils.deps import get_current_user_optional, get_current_user_required
from utils.roles import require_admin, require_moderator

from .admin import router as admin_router
from .moderator import router as moderator_router
from .public import router as public_router
from .user import router as user_router

import config

router = APIRouter(include_in_schema=False)

router.include_router(admin_router)
router.include_router(moderator_router)
router.include_router(public_router)
router.include_router(user_router)

templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))

# -------------------------
# ROOT
# -------------------------
@router.get("/", response_class=HTMLResponse)
async def root_index(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "user": user}
    )

# -------------------------
# PUBLIC
# -------------------------
@router.get("/public", response_class=HTMLResponse)
async def public_index(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse(
        "public/index.html",
        {"request": request, "user": user}
    )

# -------------------------
# USER
# -------------------------
@router.get("/user", response_class=HTMLResponse)
async def user_index(request: Request, user=Depends(get_current_user_required)):
    return templates.TemplateResponse(
        "user/index.html",
        {"request": request, "user": user}
    )

# -------------------------
# MODERATOR
# -------------------------
@router.get("/moderator", response_class=HTMLResponse)
async def moderator_index(request: Request, user=Depends(require_moderator)):
    return templates.TemplateResponse(
        "moderator/index.html",
        {"request": request, "user": user}
    )

# -------------------------
# ADMIN
# -------------------------
@router.get("/admin", response_class=HTMLResponse)
async def admin_index(request: Request, user=Depends(require_admin)):  # must be admin
    return templates.TemplateResponse(
        "admin/index.html",
        {"request": request, "user": user}
    )