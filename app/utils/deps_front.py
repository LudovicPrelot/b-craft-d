# utils/deps_front.py
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from utils.deps import get_current_user_optional
from utils.roles import _is_admin, _is_moderator
from fastapi.templating import Jinja2Templates
import config

async def front_login_required(request: Request, user=Depends(get_current_user_optional)):
    if user is None:
        return RedirectResponse(url="/forbidden")
    return user

async def front_admin_required(request: Request, user=Depends(front_login_required)):
    if user is None or not _is_admin(user):
        return RedirectResponse(url="/forbidden")
    return user

async def front_moderator_required(request: Request, user=Depends(front_login_required)):
    if user is None or not _is_moderator(user):
        return RedirectResponse(url="/forbidden")
    return user


templates_public = Jinja2Templates(directory=str(config.PUBLIC_TEMPLATES_DIR))
templates_user = Jinja2Templates(directory=str(config.USER_TEMPLATES_DIR))
templates_moderator = Jinja2Templates(directory=str(config.MODERATOR_TEMPLATES_DIR))
templates_admin = Jinja2Templates(directory=str(config.ADMIN_TEMPLATES_DIR))

def get_public_templates():
    return templates_public

def get_user_templates():
    return templates_user

def get_moderator_templates():
    return templates_moderator

def get_admin_templates():
    return templates_admin
