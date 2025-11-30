# app/routes/front/moderator/professions.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps_front import front_moderator_required, get_moderator_templates
from utils.client import api_get
import config
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/professions")

@router.get("/", response_class=HTMLResponse)
async def moderator_professions_page(request: Request, user=Depends(front_moderator_required), templates = Depends(get_moderator_templates)):
    professions = api_get("/api/public/professions")

    return templates.TemplateResponse(
        "professions/index.html",
        {"request": request, "user": user, "professions": professions}
    )
