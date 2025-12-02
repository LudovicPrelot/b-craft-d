# app/routes/front/public/resources.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps import get_current_user_optional
from utils.deps_front import get_templates

router = APIRouter(prefix="/resources", include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
async def public_resources_page(
    request: Request,
    user=Depends(get_current_user_optional),
    templates = Depends(get_templates)
):
    return templates.TemplateResponse(
        "public/resources/index.html",
        {"request": request, "user": user}
    )