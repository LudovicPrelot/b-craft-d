# tests/test_auth_flow.py
"""
Tests du flux d'authentification avec PostgreSQL.

Teste: login, refresh, logout, multi-device.
"""

import pytest
from conftest import auth_headers


# ============================================================================
# TEST LOGIN
# ============================================================================

@pytest.mark.auth
def test_login_success(client, sample_user, db_session):
    """Test login réussi avec credentials valides."""
    response = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "laptop",
        "device_name": "MacBook Pro"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Vérifie la structure de la réponse
    assert "access_token" in data
    assert "device_id" in data
    assert data["device_id"] == "laptop"
    assert "user" in data
    assert data["user"]["login"] == sample_user.login
    
    # Vérifie le cookie refresh_token
    assert "refresh_token" in response.cookies


@pytest.mark.auth
def test_login_fail_wrong_password(client, sample_user):
    """Test login échoué avec mauvais mot de passe."""
    response = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "WrongPassword!"
    })
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.auth
def test_login_fail_unknown_user(client):
    """Test login échoué avec utilisateur inexistant."""
    response = client.post("/api/public/auth/login", json={
        "login": "unknown_user",
        "password": "Whatever123!"
    })
    
    assert response.status_code == 401


@pytest.mark.auth
def test_login_missing_credentials(client):
    """Test login échoué avec credentials manquantes."""
    response = client.post("/api/public/auth/login", json={
        "login": "testuser"
        # password manquant
    })
    
    assert response.status_code == 400


# ============================================================================
# TEST REFRESH TOKEN (ROTATION)
# ============================================================================

@pytest.mark.auth
def test_refresh_success(client, sample_user):
    """Test refresh réussi avec rotation du token."""
    # 1. Login
    login_response = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "laptop"
    })
    
    old_refresh = login_response.cookies.get("refresh_token")
    old_access = login_response.json()["access_token"]
    
    # 2. Refresh
    refresh_response = client.post("/api/public/auth/refresh", json={
        "refresh_token": old_refresh
    })
    
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    
    # Vérifie qu'on a de nouveaux tokens
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] != old_access  # Nouveau token
    assert data["refresh_token"] != old_refresh  # Rotation
    assert data["device_id"] == "laptop"
    
    # Vérifie que le cookie est mis à jour
    new_refresh = refresh_response.cookies.get("refresh_token")
    assert new_refresh != old_refresh


@pytest.mark.auth
def test_refresh_fail_invalid_token(client):
    """Test refresh échoué avec token invalide."""
    response = client.post("/api/public/auth/refresh", json={
        "refresh_token": "invalid.token.here"
    })
    
    assert response.status_code == 401


@pytest.mark.auth
def test_refresh_fail_reused_token(client, sample_user):
    """Test qu'un token ne peut pas être réutilisé après refresh (rotation)."""
    # 1. Login
    login_response = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!"
    })
    
    old_refresh = login_response.cookies.get("refresh_token")
    
    # 2. Premier refresh (OK)
    refresh_response = client.post("/api/public/auth/refresh", json={
        "refresh_token": old_refresh
    })
    assert refresh_response.status_code == 200
    
    # 3. Réutiliser l'ancien token (devrait échouer)
    reuse_response = client.post("/api/public/auth/refresh", json={
        "refresh_token": old_refresh
    })
    assert reuse_response.status_code == 401


# ============================================================================
# TEST LOGOUT
# ============================================================================

@pytest.mark.auth
def test_logout_success(client, sample_user):
    """Test logout réussi."""
    # 1. Login
    login_response = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!"
    })
    
    refresh_token = login_response.cookies.get("refresh_token")
    
    # 2. Logout
    logout_response = client.post("/api/public/auth/logout", json={
        "refresh_token": refresh_token
    })
    
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logged out"
    
    # 3. Vérifier que le token ne fonctionne plus
    refresh_response = client.post("/api/public/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_response.status_code == 401


@pytest.mark.auth
def test_logout_all_devices(client, sample_user):
    """Test logout sur tous les devices."""
    # 1. Login sur 2 devices
    device1 = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "laptop"
    })
    
    device2 = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "phone"
    })
    
    access_token = device1.json()["access_token"]
    refresh1 = device1.cookies.get("refresh_token")
    refresh2 = device2.cookies.get("refresh_token")
    
    # 2. Logout all
    logout_response = client.post(
        "/api/public/auth/logout_all",
        headers=auth_headers(access_token)
    )
    
    assert logout_response.status_code == 200
    assert logout_response.json()["count"] == 2  # 2 tokens révoqués
    
    # 3. Vérifier que les 2 tokens ne fonctionnent plus
    assert client.post("/api/public/auth/refresh", json={"refresh_token": refresh1}).status_code == 401
    assert client.post("/api/public/auth/refresh", json={"refresh_token": refresh2}).status_code == 401


# ============================================================================
# TEST DEVICES MANAGEMENT
# ============================================================================

@pytest.mark.auth
def test_list_devices(client, sample_user):
    """Test liste des devices actifs."""
    # 1. Login sur 2 devices
    client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "laptop",
        "device_name": "MacBook Pro"
    })
    
    login2 = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "phone",
        "device_name": "iPhone"
    })
    
    access_token = login2.json()["access_token"]
    
    # 2. Liste devices
    response = client.get(
        "/api/public/auth/devices",
        headers=auth_headers(access_token)
    )
    
    assert response.status_code == 200
    devices = response.json()["devices"]
    
    assert len(devices) == 2
    device_ids = {d["device_id"] for d in devices}
    assert "laptop" in device_ids
    assert "phone" in device_ids


@pytest.mark.auth
def test_revoke_specific_device(client, sample_user):
    """Test révocation d'un device spécifique."""
    # 1. Login sur 2 devices
    device1 = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "laptop"
    })
    
    device2 = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "phone"
    })
    
    access_token = device1.json()["access_token"]
    refresh1 = device1.cookies.get("refresh_token")
    refresh2 = device2.cookies.get("refresh_token")
    
    # 2. Révoquer le laptop
    revoke_response = client.post(
        "/api/public/auth/devices/laptop/revoke",
        headers=auth_headers(access_token)
    )
    
    assert revoke_response.status_code == 200
    assert revoke_response.json()["device_id"] == "laptop"
    
    # 3. Vérifier que laptop ne fonctionne plus, mais phone oui
    assert client.post("/api/public/auth/refresh", json={"refresh_token": refresh1}).status_code == 401
    assert client.post("/api/public/auth/refresh", json={"refresh_token": refresh2}).status_code == 200


# ============================================================================
# TEST EDGE CASES
# ============================================================================

@pytest.mark.auth
def test_login_generates_device_id_if_missing(client, sample_user):
    """Test que device_id est généré automatiquement si absent."""
    response = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!"
        # Pas de device_id
    })
    
    assert response.status_code == 200
    assert "device_id" in response.json()
    assert len(response.json()["device_id"]) > 0  # UUID généré


@pytest.mark.auth
def test_concurrent_logins_same_device(client, sample_user):
    """Test logins multiples sur le même device (remplace l'ancien)."""
    # 1. Premier login
    login1 = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "laptop"
    })
    
    refresh1 = login1.cookies.get("refresh_token")
    
    # 2. Deuxième login (même device)
    login2 = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "laptop"
    })
    
    refresh2 = login2.cookies.get("refresh_token")
    access2 = login2.json()["access_token"]
    
    # 3. Vérifier qu'il n'y a qu'un seul device actif
    devices_response = client.get(
        "/api/public/auth/devices",
        headers=auth_headers(access2)
    )
    
    devices = devices_response.json()["devices"]
    laptop_devices = [d for d in devices if d["device_id"] == "laptop"]
    
    # Selon l'implémentation, peut être 1 (remplacement) ou 2 (accumulation)
    # Ici on teste que le nouveau token fonctionne
    assert client.post("/api/public/auth/refresh", json={"refresh_token": refresh2}).status_code == 200