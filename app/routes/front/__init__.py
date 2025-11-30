# app/routes/front/__init__.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from utils.deps import get_current_user_optional, get_current_user_required
from utils.roles import require_admin, require_moderator

import config

router = APIRouter()
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
# ADMIN
# -------------------------
@router.get("/admin", response_class=HTMLResponse)
async def admin_index(
    request: Request,
    user=Depends(require_admin)  # must be admin
):
    return templates.TemplateResponse(
        "admin/index.html",
        {"request": request, "user": user}
    )