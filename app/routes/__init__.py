# routes/__init__.py

from .auth_routes import router as auth_router
from .users_routes import router as users_router
from .admin_routes import router as admin_router
from .admin_settings_routes import router as admin_settings_router
from .professions_routes import router as professions_router
from .recipes_routes import router as recipes_router
from .resources_routes import router as resources_router
from .inventory_routes import router as inventory_router
from .loot_routes import router as loot_router
from .quests_routes import router as quests_router
from .crafting_routes import router as crafting_router
from .stats_routes import router as stats_router
from .public_routes import router as public_api_router
from .pages_routes import router as pages_router
from .devices_routes import router as devices_router

__all__ = [
    "auth_router", "users_router", "admin_router", "admin_settings_router",
    "professions_router", "recipes_router", "resources_router",
    "inventory_router", "loot_router", "quests_router", "crafting_router",
    "stats_router", "public_api_router", "pages_router", "devices_router"
]
