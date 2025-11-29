# app/routes/pages_routes.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from utils.logger import get_logger
import config
from fastapi.templating import Jinja2Templates

from utils.deps import get_current_user_optional, get_current_user_required

logger = get_logger(__name__)

router = APIRouter(prefix="", tags=["Front Pages"])

templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


@router.get("/home", response_class=HTMLResponse)
def page_index(request: Request, user=Depends(get_current_user_optional)):
    logger.debug(f"🏠 Accès à la page index (user: {user.get('login') if user else 'anonymous'})")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user}
    )


@router.get("/login", response_class=HTMLResponse)
def page_login(request: Request, user=Depends(get_current_user_optional)):
    if user:
        logger.debug(f"🔄 Redirection vers profile (user déjà connecté: {user.get('login')})")
        return RedirectResponse("/pages/profile")
    
    logger.debug("🔑 Accès à la page de connexion")
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.get("/register", response_class=HTMLResponse)
def page_register(request: Request):
    logger.debug("📝 Accès à la page d'inscription")
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse)
def page_profile(request: Request, user=Depends(get_current_user_required)):
    logger.debug(f"👤 Accès au profil de {user.get('login')}")
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user}
    )