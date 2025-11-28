# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# import routers directly to avoid circulars
from routes.auth_routes import router as auth_router
from routes.users_routes import router as users_router
from routes.admin_routes import router as admin_router
from routes.admin_settings_routes import router as admin_settings_router
from routes.professions_routes import router as professions_router
from routes.recipes_routes import router as recipes_router
from routes.resources_routes import router as resources_router
from routes.inventory_routes import router as inventory_router
from routes.loot_routes import router as loot_router
from routes.quests_routes import router as quests_router
from routes.crafting_routes import router as crafting_router
from routes.stats_routes import router as stats_router
from routes.public_routes import router as public_api_router
from routes.pages_routes import router as pages_router
from routes.devices_routes import router as devices_router

app = FastAPI(title="Craft Game")

# static files (JS/CSS)
app.mount("/static", StaticFiles(directory="web_interface/static"), name="static")

# include API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(admin_settings_router)
app.include_router(professions_router)
app.include_router(recipes_router)
app.include_router(resources_router)
app.include_router(inventory_router)
app.include_router(loot_router)
app.include_router(quests_router)
app.include_router(crafting_router)
app.include_router(stats_router)
app.include_router(public_api_router)
app.include_router(pages_router)
app.include_router(devices_router)
