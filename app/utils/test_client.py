# app/utils/test_client.py
"""
Remplacement du local_api_dispatcher par TestClient de FastAPI.

Usage:
    from utils.test_client import test_client
    
    # Au lieu de:
    # result = await api_get("/api/public/professions")
    
    # Utiliser:
    response = test_client.get("/api/public/professions")
    result = response.json()
"""

from fastapi.testclient import TestClient
from main import app

# Instance TestClient globale (réutilisable)
test_client = TestClient(app)


# ============================================================================
# Helpers pour compatibilité avec l'ancien code (optionnel)
# ============================================================================

def sync_get(endpoint: str, **kwargs):
    """
    GET synchrone avec TestClient.
    
    Args:
        endpoint: URL relative (ex: "/api/public/professions")
        **kwargs: Paramètres supplémentaires (headers, params, etc.)
    
    Returns:
        Response object de TestClient
    
    Example:
        response = sync_get("/api/public/professions")
        data = response.json()
    """
    return test_client.get(endpoint, **kwargs)


def sync_post(endpoint: str, json_data=None, **kwargs):
    """
    POST synchrone avec TestClient.
    
    Args:
        endpoint: URL relative
        json_data: Dict à envoyer en JSON
        **kwargs: Paramètres supplémentaires
    
    Returns:
        Response object
    
    Example:
        response = sync_post("/api/admin/professions/", json_data={
            "id": "mineur",
            "name": "Mineur"
        })
    """
    return test_client.post(endpoint, json=json_data, **kwargs)


def sync_put(endpoint: str, json_data=None, **kwargs):
    """PUT synchrone avec TestClient."""
    return test_client.put(endpoint, json=json_data, **kwargs)


def sync_patch(endpoint: str, json_data=None, **kwargs):
    """PATCH synchrone avec TestClient."""
    return test_client.patch(endpoint, json=json_data, **kwargs)


def sync_delete(endpoint: str, **kwargs):
    """DELETE synchrone avec TestClient."""
    return test_client.delete(endpoint, **kwargs)


# ============================================================================
# Wrapper pour authentification (helper)
# ============================================================================

def with_auth(token: str):
    """
    Retourne un dict de headers avec Authorization.
    
    Usage:
        token = login_and_get_token()
        response = test_client.get("/api/user/me", headers=with_auth(token))
    """
    return {"Authorization": f"Bearer {token}"}


def login_and_get_token(login: str = "testuser", password: str = "test123"):
    """
    Helper pour se connecter et obtenir un access_token.
    
    Usage dans tests:
        token = login_and_get_token("admin", "admin123")
        response = test_client.get("/api/admin/users", headers=with_auth(token))
    """
    response = test_client.post("/api/public/auth/login", json={
        "login": login,
        "password": password
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")


# ============================================================================
# Exemple d'utilisation complète
# ============================================================================

if __name__ == "__main__":
    """
    Exemple d'utilisation du test_client.
    Peut être exécuté avec: python -m utils.test_client
    """
    
    print("=" * 70)
    print("EXEMPLE D'UTILISATION DE TEST_CLIENT")
    print("=" * 70)
    
    # Test 1: Route publique sans auth
    print("\n1. Test route publique (sans auth)")
    response = test_client.get("/api/public/professions")
    print(f"   Status: {response.status_code}")
    print(f"   Professions: {len(response.json())} trouvées")
    
    # Test 2: Login et route authentifiée
    print("\n2. Test login + route authentifiée")
    try:
        token = login_and_get_token("admin", "admin")
        print(f"   Token obtenu: {token[:30]}...")
        
        response = test_client.get("/api/user/me", headers=with_auth(token))
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"   User: {user.get('login')}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test 3: Route admin (nécessite is_admin=True)
    print("\n3. Test route admin")
    response = test_client.get("/api/admin/professions/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   ✅ Authentification requise (normal)")
    
    print("\n" + "=" * 70)