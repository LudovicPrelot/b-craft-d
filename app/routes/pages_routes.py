# routes/pages_routes.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from utils.deps import require_user
from utils.roles import require_role_admin
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "web_interface/templates"))

router = APIRouter(tags=["Pages"])

# -------------------------
# Public pages (no auth)
# -------------------------
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/public/resources", response_class=HTMLResponse)
def public_resources(request: Request):
    return templates.TemplateResponse("public/resources.html", {"request": request})

@router.get("/public/recipes", response_class=HTMLResponse)
def public_recipes(request: Request):
    return templates.TemplateResponse("public/recipes.html", {"request": request})

@router.get("/public/professions", response_class=HTMLResponse)
def public_professions(request: Request):
    return templates.TemplateResponse("public/professions.html", {"request": request})

# -------------------------
# User pages (auth required)
# -------------------------
@router.get("/me", response_class=HTMLResponse)
def me_page(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse("me.html", {"request": request, "user": user})

@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@router.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse("inventory.html", {"request": request})

@router.get("/crafting", response_class=HTMLResponse)
def crafting_page(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse("crafting.html", {"request": request})

@router.get("/devices", response_class=HTMLResponse)
def devices_page(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse("devices.html", {"request": request})

# -------------------------
# Admin pages (admin only)
# -------------------------
@router.get("/admin", response_class=HTMLResponse, dependencies=[Depends(require_role_admin)])
def admin_index(request: Request):
    return templates.TemplateResponse("admin/index.html", {"request": request})

@router.get("/admin/users", response_class=HTMLResponse, dependencies=[Depends(require_role_admin)])
def admin_users(request: Request):
    return templates.TemplateResponse("admin/users.html", {"request": request})

@router.get("/admin/resources", response_class=HTMLResponse, dependencies=[Depends(require_role_admin)])
def admin_resources(request: Request):
    return templates.TemplateResponse("admin/resources.html", {"request": request})

@router.get("/admin/recipes", response_class=HTMLResponse, dependencies=[Depends(require_role_admin)])
def admin_recipes(request: Request):
    return templates.TemplateResponse("admin/recipes.html", {"request": request})

@router.get("/admin/professions", response_class=HTMLResponse, dependencies=[Depends(require_role_admin)])
def admin_professions(request: Request):
    return templates.TemplateResponse("admin/professions.html", {"request": request})

@router.get("/admin/loot", response_class=HTMLResponse, dependencies=[Depends(require_role_admin)])
def admin_loot(request: Request):
    return templates.TemplateResponse("admin/loot.html", {"request": request})

@router.get("/admin/stats", response_class=HTMLResponse, dependencies=[Depends(require_role_admin)])
def admin_stats(request: Request):
    return templates.TemplateResponse("admin/stats.html", {"request": request})

@router.get("/admin/settings", response_class=HTMLResponse, dependencies=[Depends(require_role_admin)])
def admin_settings(request: Request):
    return templates.TemplateResponse("admin/settings.html", {"request": request})
