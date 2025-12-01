# app/routes/front/user/professions.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps import get_current_user_required
from utils.deps_front import get_templates

router = APIRouter(prefix="/professions", include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
async def user_professions_page(
    request: Request,
    user=Depends(get_current_user_required),
    templates = Depends(get_templates)
):
    return templates.TemplateResponse(
        "user/professions/index.html",
        {"request": request, "user": user}
    )
