from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from utils.deps import get_current_moderator
from utils.templates import get_templates

router = APIRouter(prefix="/moderator")

@router.get("/", response_class=HTMLResponse)
async def moderator_home(request: Request, user=Depends(get_current_moderator), templates = Depends(get_templates)):
    return templates.TemplateResponse("moderator/index.html", {"request": request, "user": user})
