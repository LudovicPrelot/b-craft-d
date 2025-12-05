# app/main.py (VERSION POSTGRESQL)
"""
Point d'entrée FastAPI principal avec PostgreSQL.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from utils.logger import get_logger
from utils.auth import cleanup_expired_tokens
from utils.settings import init_default_settings
from utils.feature_flags import init_feature_flags
from database.connection import SessionLocal, init_db, check_db_connection

# API Routers
from routes.api import router as api_router

# FRONT Routers
from routes.front import router as front_router

import config

logger = get_logger(__name__)


# ============================================================================
# LIFESPAN (remplace les events startup/shutdown)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application.
    - startup: Initialise la DB + nettoie les tokens expirés
    - shutdown: Nettoyage si nécessaire
    """
    # STARTUP
    logger.info("🚀 Démarrage de B-CraftD...")
    
    # Vérifie la connexion DB
    if not check_db_connection():
        logger.error("❌ Impossible de se connecter à PostgreSQL")
        raise RuntimeError("Database connection failed")
    
    # Initialise les tables
    init_db()
    
    
    try:
        db = SessionLocal()
        # deleted = cleanup_expired_tokens(db) # Nettoie les tokens expirés au démarrage
        # if deleted > 0:
        #     logger.info(f"🧹 {deleted} refresh token(s) expiré(s) nettoyé(s)")
        
        # init_feature_flags(db)  # Crée les feature flags par défaut
        # init_default_settings(db)  # Crée les settings par défaut
        db.close()

    except Exception as e:
        logger.warning(f"⚠️  Erreur lors du nettoyage des tokens: {e}")

    yield
    
    logger.info("✅ Application prête!")
    
    # SHUTDOWN
    logger.info("👋 Arrêt de l'application...")


# ============================================================================
# APP
# ============================================================================

app = FastAPI(
    title="B-CraftD – Backend + Front",
    description="API pour un système de crafting réaliste avec PostgreSQL",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # ✅ Remplace @app.on_event("startup")
)

logger.info("🏗️  Initialisation de l'application FastAPI")

# -------------------------
# Static + templates
# -------------------------
logger.debug(f"📁 Montage des fichiers statiques depuis {config.STATIC_DIR}")
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


# -------------------------
# Exception Handlers
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
# Middleware de logging
# -------------------------

@app.middleware("http")
async def front_security_middleware(request: Request, call_next):
    try:
        response = await call_next(request)

        if response.status_code == 401:
            return RedirectResponse("/public/login")
        if response.status_code == 403:
            return templates.TemplateResponse("errors/403.html", {"request": request})
        if response.status_code == 404:
            return templates.TemplateResponse("errors/404.html", {"request": request})
        if response.status_code == 500:
            return templates.TemplateResponse("errors/500.html", {"request": request})

        return response

    except PermissionError:
        return RedirectResponse("/public/login")
    except Exception:
        return templates.TemplateResponse("errors/500.html", {"request": request})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes HTTP entrantes."""
    logger.debug(f"📥 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    logger.debug(f"📤 {request.method} {request.url.path} → {response.status_code}")
    return response


# --------------------------------------
# Routers
# --------------------------------------
app.include_router(api_router)
app.include_router(front_router)


# -------------------------
# Error handlers
# -------------------------

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    """Log toutes les erreurs 404."""
    logger.debug(f"⚠️  Erreur 404 sur {request.method} {request.url.path}")
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )


@app.exception_handler(500)
async def custom_500_handler(request, exc):
    """Log toutes les erreurs 500."""
    logger.debug(f"⚠️  Erreur 500 sur {request.method} {request.url.path}")
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request, "message": str(exc)},
        status_code=500
    )


# -------------------------
# Health check
# -------------------------

@app.get("/health")
def health_check():
    """Endpoint de santé pour monitoring."""
    db_ok = check_db_connection()
    
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "version": "0.2.0"
    }


logger.info("✅ Application FastAPI prête!")
logger.info(f"📚 Documentation API disponible sur /docs et /redoc")