# app/main.py
"""
Chemin : app/main.py

Point d'entrée FastAPI.
 - Monte les fichiers statiques du FRONT
 - Configure les templates Jinja2
 - Inclut les routes API
 - Inclut routes/pages_routes.py pour le FRONT
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import config
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

app = FastAPI(title="B-CraftD — Backend + Front")

# -------------------------
# Static + templates
# -------------------------
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))

# -------------------------
# Redirect root → index.html
# -------------------------
@app.get("/")
def root():
    return RedirectResponse("/pages/index")


# -------------------------
# API routers
# -------------------------
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
app.include_router(pages_router)
