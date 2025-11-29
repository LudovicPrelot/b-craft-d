# app/main.py
"""
Point d'entrée FastAPI.
 - Monte les fichiers statiques du FRONT
 - Configure les templates Jinja2
 - Inclut les routes API
 - Inclut routes/pages_routes.py pour le FRONT
 - Configure le logging et la gestion d'erreurs
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

import config
from utils.logger import get_logger
from routes import (
    auth_routes,
    users_routes,
    resources_routes,
    recipes_routes,
    professions_routes,
    inventory_routes,
    crafting_routes,
    loot_routes,
    stats_routes,
    quests_routes,
    public_routes,
    admin_routes,
    admin_settings_routes,
)
from routes.pages_routes import router as pages_router

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


# -------------------------
# Redirect root → index.html
# -------------------------
@app.get("/")
def root():
    logger.debug("🏠 Redirection de / vers /home")
    return RedirectResponse("/home")


# -------------------------
# API routers
# -------------------------
logger.info("📦 Chargement des routes API...")
app.include_router(auth_routes.router)
app.include_router(users_routes.router)
app.include_router(resources_routes.router)
app.include_router(recipes_routes.router)
app.include_router(professions_routes.router)
app.include_router(inventory_routes.router)
app.include_router(crafting_routes.router)
app.include_router(loot_routes.router)
app.include_router(stats_routes.router)
app.include_router(quests_routes.router)
app.include_router(public_routes.router)
app.include_router(admin_routes.router)
app.include_router(admin_settings_routes.router)

# -------------------------
# Pages HTML
# -------------------------
logger.info("🌐 Chargement des routes de pages HTML...")
app.include_router(pages_router)

logger.info("✅ Application FastAPI prête!")
logger.info(f"📚 Documentation API disponible sur /docs et /redoc")