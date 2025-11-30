# routes/__init__.py

from .api import router as api_router
from .front import router as front_router

__all__ = [
    "api_router",
    "front_router"
]
