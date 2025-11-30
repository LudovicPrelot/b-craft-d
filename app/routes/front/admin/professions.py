# app/routes/front/admin/professions.py

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from utils.deps_front import front_admin_required, get_admin_templates
from utils.client import api_get, api_post, api_delete
import config
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/professions")

@router.get("/", response_class=HTMLResponse)
async def admin_professions_page(request: Request, user=Depends(front_admin_required), templates = Depends(get_admin_templates)):
    professions = api_get("/api/public/professions")

    return templates.TemplateResponse(
        "professions/index.html",
        {"request": request, "user": user, "professions": professions}
    )

@router.post("/create")
async def admin_professions_create(name: str = Form(...), user=Depends(front_admin_required)):
    api_post("/api/admin/professions/", {"name": name})
    return RedirectResponse("/admin/professions", status_code=303)

@router.post("/admin/professions/{pid}/delete")
async def admin_professions_delete(pid: str, user=Depends(front_admin_required)):
    api_delete(f"/api/admin/professions/{pid}")
    return RedirectResponse("/admin/professions", status_code=303)
