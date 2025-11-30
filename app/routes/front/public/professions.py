# app/routes/front/public/professions.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps import get_current_user_optional
from utils.deps_front import get_public_templates
from utils.client import api_get
import config

router = APIRouter(prefix="/professions", include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
async def public_professions_page(request: Request, user=Depends(get_current_user_optional), templates = Depends(get_public_templates)):
    professions = api_get("/api/public/professions")

    return templates.TemplateResponse(
        "professions/index.html",
        {"request": request, "user": user, "professions": professions}
    )
