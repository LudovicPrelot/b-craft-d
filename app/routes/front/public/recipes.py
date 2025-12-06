# app/routes/front/public/recipes.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps import get_current_user_optional
from utils.deps_front import get_templates

router = APIRouter(prefix="/recipes", include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
async def public_recipes_page(
    request: Request,
    user=Depends(get_current_user_optional),
    templates = Depends(get_templates)
):
    return templates.TemplateResponse(
        "public/recipes/index.html",
        {"request": request, "user": user}
    )
