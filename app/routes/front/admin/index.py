from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps import get_current_admin
from utils.templates import get_templates

router = APIRouter(prefix="/admin")

@router.get("/", response_class=HTMLResponse)
async def admin_home(request: Request, user=Depends(get_current_admin), templates = Depends(get_templates)):
    return templates.TemplateResponse("admin/index.html", {"request": request, "user": user})
