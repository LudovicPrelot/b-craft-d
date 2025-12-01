# utils/deps_front.py
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from utils.deps import get_current_user_optional
from utils.roles import require_admin, require_moderator
from fastapi.templating import Jinja2Templates
import config

async def front_login_required(request: Request, user=Depends(get_current_user_optional)):
    if user is None:
        return RedirectResponse(url="/forbidden")
    return user

async def front_admin_required(request: Request, user=Depends(front_login_required)):
    if user is None or not require_admin(user):
        return RedirectResponse(url="/forbidden")
    return user

async def front_moderator_required(request: Request, user=Depends(front_login_required)):
    if user is None or not require_moderator(user):
        return RedirectResponse(url="/forbidden")
    return user

templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))

def get_templates():
    return templates


