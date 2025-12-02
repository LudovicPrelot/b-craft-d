# app/routes/front/admin/professions.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps import get_current_admin
from utils.deps_front import get_templates

router = APIRouter(prefix="/professions", include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
async def admin_professions_page(
    request: Request,
    user=Depends(get_current_admin),
    templates = Depends(get_templates)
):
    return templates.TemplateResponse(
        "admin/professions/index.html",
        {"request": request, "user": user}
    )