# utils/feature_flags.py
from fastapi import HTTPException, Depends
from utils.settings import get_settings

def require_feature(name: str):
    """
    Returns a FastAPI dependency that raises 403 if a feature is disabled.
    Usage:
    @router.get("/something", dependencies=[Depends(require_feature("enable_loot"))])
    """
    def _dependency():
        settings = get_settings()
        if not settings.get(name, False):
            raise HTTPException(403, f"Feature '{name}' is disabled.")
    return _dependency
