# app/main.py
"""
Point d'entrée FastAPI principal.
 - Gère le routing global
 - Charge les templates Jinja2
 - Monte les fichiers statiques
 - Ajoute middlewares + logging + handlers d’erreurs
 - Sépare API et routes FRONT (pages/)
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils.logger import get_logger
from scripts import fix_bugs as fix_bugs

# API Routers
from routes.api import router as api_router

# FRONT Routers (nouveaux)
from routes.front import router as front_router

import config

# Initialise le logger pour ce module
logger = get_logger(__name__)

app = FastAPI(
    title="B-CraftD – Backend + Front",
    description="API pour un système de crafting réaliste",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger.info("🏗️  Initialisation de l'application FastAPI")

# -------------------------
# Static + templates
# -------------------------
logger.debug(f"📁 Montage des fichiers statiques depuis {config.STATIC_DIR}")
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


# -------------------------
# Exception Handlers (gestion d'erreurs centralisée)
# -------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gère toutes les exceptions non capturées."""
    logger.error(
        f"❌ Erreur non gérée sur {request.method} {request.url.path}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if config.DEBUG else "An unexpected error occurred"
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Gère les exceptions HTTP (404, 403, etc.)."""
    logger.warning(
        f"⚠️  HTTP {exc.status_code} sur {request.method} {request.url.path}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gère les erreurs de validation Pydantic."""
    logger.warning(
        f"⚠️  Erreur de validation sur {request.method} {request.url.path}: {exc.errors()}"
    )
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()}
    )


# -------------------------
# Middleware de logging des requêtes
# -------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes HTTP entrantes."""
    logger.debug(f"📥 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    logger.debug(f"📤 {request.method} {request.url.path} → {response.status_code}")
    return response


# --------------------------------------
# API Routers
# --------------------------------------
app.include_router(api_router)

logger.info("🌐 Chargement des routes de pages HTML...")
# --------------------------------------
# FRONT Routers (Pages HTML)
# --------------------------------------
app.include_router(front_router)

# -------------------------
# Debug script
# -------------------------

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    """Log toutes les erreurs 404."""
    logger.debug( f"⚠️  Erreur 404 sur {request.method} {request.url.path}")
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def custom_500_handler(request, exc):
    """Log toutes les erreurs 500."""
    logger.debug( f"⚠️  Erreur 500 sur {request.method} {request.url.path}")
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request, "message": str(exc)},
        status_code=500
    )


fix_bugs

logger.info("✅ Application FastAPI prête!")
logger.info(f"📚 Documentation API disponible sur /docs et /redoc")