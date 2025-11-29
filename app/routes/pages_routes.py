# app/routes/pages_routes.py
"""
Chemin : app/routes/pages_routes.py

Routes FRONT (pages HTML)
 - index
 - login
 - register
 - profile (protégé)
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

import config
from fastapi.templating import Jinja2Templates

from utils.deps import get_current_user_optional, get_current_user_required

router = APIRouter(prefix="/pages", tags=["Front Pages"])

templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


@router.get("/index", response_class=HTMLResponse)
def page_index(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user}
    )


@router.get("/login", response_class=HTMLResponse)
def page_login(request: Request, user=Depends(get_current_user_optional)):
    # si déjà connecté → page profile
    if user:
        return RedirectResponse("/pages/profile")
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.get("/register", response_class=HTMLResponse)
def page_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse)
def page_profile(request: Request, user=Depends(get_current_user_required)):
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user}
    )
