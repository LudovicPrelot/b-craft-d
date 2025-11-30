# app/routes/api/user/__init__.py

from fastapi import APIRouter
from .crafting import router as crafting_router
from .dashboard import router as dashboard_router
from .devices import router as devices_router
from .inventory import router as inventory_router
from .loot import router as loot_router
from .me import router as me_router
from .professions import router as professions_router
from .quests import router as quests_router
from .recipes import router as recipes_router
from .resources import router as resources_router
from .stats import router as stats_router

router = APIRouter(prefix="/user")

router.include_router(crafting_router)
router.include_router(dashboard_router)
router.include_router(devices_router)
router.include_router(inventory_router)
router.include_router(loot_router)
router.include_router(me_router)
router.include_router(professions_router)
router.include_router(quests_router)
router.include_router(recipes_router)
router.include_router(resources_router)
router.include_router(stats_router)

