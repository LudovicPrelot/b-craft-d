# app/routes/front/moderator/professions.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps import get_current_moderator
from utils.deps_front import get_templates

router = APIRouter(prefix="/professions", include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
async def moderator_professions_page(
    request: Request,
    user=Depends(get_current_moderator),
    templates = Depends(get_templates)
):
    return templates.TemplateResponse(
        "moderator/professions/index.html",
        {"request": request, "user": user}
    )
