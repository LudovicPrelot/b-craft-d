"""
Admin - Dispatcher Inspection
Permet de voir :
 - Les routes connues du dispatcher local
 - Tester un endpoint via HTTP ou fallback local
"""

from fastapi import APIRouter, Depends, Query
from utils.roles import require_admin
from utils.local_api_dispatcher import LOCAL_REGISTRY, call_local_sync
from utils.client import api_get, api_post, api_put, api_delete
from config import ENABLE_LOCAL_FALLBACK

router = APIRouter(prefix="/dispatcher", tags=["Admin - Dispatcher"])


# ---------------------------------------------------------
# GET /api/admin/dispatcher/
# ---------------------------------------------------------
@router.get("/", summary="Inspect Dispatcher Registry")
async def dispatcher_registry(user=Depends(require_admin)):
    """
    Retourne la liste des routes du dispatcher local.
    """

    registry = [
        {
            "method": method,
            "path": path,
            "handler": f"{handler.__module__}.{handler.__name__}"
        }
        for (method, path), handler in LOCAL_REGISTRY.items()
    ]

    return {
        "fallback_enabled": ENABLE_LOCAL_FALLBACK,
        "count": len(registry),
        "routes": registry,
    }


# ---------------------------------------------------------
# GET /api/admin/dispatcher/test
# ---------------------------------------------------------
@router.get("/test", summary="Test dispatcher resolution")
async def dispatcher_test(
    user=Depends(require_admin),
    endpoint: str = Query(..., description="Ex: /api/public/professions"),
    method: str = Query("GET"),
):
    """
    Teste une route API :
    - d’abord via HTTP client
    - en fallback local si activé
    """

    method = method.upper()

    # ---- Réalisation de la requête HTTP ----
    try:
        if method == "GET":
            http_result = await api_get(endpoint, require_auth=False)
        elif method == "POST":
            http_result = await api_post(endpoint, {}, require_auth=False)
        elif method == "PUT":
            http_result = await api_put(endpoint, {}, require_auth=False)
        elif method == "DELETE":
            http_result = await api_delete(endpoint, require_auth=False)
        else:
            return {"error": f"Unsupported method: {method}"}

        return {
            "mode": "HTTP",
            "result": http_result
        }

    except Exception as e:
        # Erreur HTTP → fallback local si activé
        if not ENABLE_LOCAL_FALLBACK:
            return {"error": str(e), "mode": "HTTP_ONLY"}

        # Fallback local
        local_result = call_local_sync(endpoint, method=method)
        return {
            "mode": "LOCAL_FALLBACK",
            "result": local_result,
            "note": "HTTP unreachable, local dispatcher used."
        }
