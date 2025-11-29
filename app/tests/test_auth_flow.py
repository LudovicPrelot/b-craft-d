# app/tests/test_auth_flow.py
import json
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
import os

from main import app
from config import USERS_FILE, REFRESH_TOKENS_FILE
from utils.json import save_json, load_json
from utils.auth import hash_password, _token_hash

client = TestClient(app)


# ----------------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------------
@pytest.fixture(autouse=True)
def cleanup_storage(tmp_path, monkeypatch):
    """
    Create isolated storage for USERS_FILE and REFRESH_TOKENS_FILE
    so tests never touch real data.
    """
    users_file = tmp_path / "users.json"
    refresh_file = tmp_path / "refresh_tokens.json"

    monkeypatch.setattr("config.USERS_FILE", users_file)
    monkeypatch.setattr("config.REFRESH_TOKENS_FILE", refresh_file)

    # empty initial store
    save_json(users_file, {})
    save_json(refresh_file, {})

    yield


@pytest.fixture
def create_user():
    def _create_user(login="test", password="pass123"):
        uid = str(uuid4())
        users = load_json(USERS_FILE)
        users[uid] = {
            "login": login,
            "password_hash": hash_password(password),
            "firstname": "Test",
            "lastname": "User",
            "mail": "t@u.com",
            "profession": "miner",
            "subclasses": [],
            "is_admin": False,
            "is_moderator": False,
        }
        save_json(USERS_FILE, users)
        return uid
    return _create_user


# ----------------------------------------------------------------------
# TEST LOGIN
# ----------------------------------------------------------------------
def test_login_success(create_user):
    uid = create_user()

    res = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
        "device_id": "pc-1",
        "device_name": "PC Windows"
    })
    assert res.status_code == 200
    data = res.json()

    assert "access_token" in data
    assert data["device_id"] == "pc-1"

    # check cookie refresh token
    assert "refresh_token" in res.cookies


def test_login_fail_wrong_password(create_user):
    create_user()

    res = client.post("/api/auth/login", json={
        "login": "test",
        "password": "wrong"
    })
    assert res.status_code == 401


# ----------------------------------------------------------------------
# TEST REFRESH (ROTATION)
# ----------------------------------------------------------------------
def test_refresh_success(create_user):
    uid = create_user()

    # 1) Login
    res = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
        "device_id": "pc-1"
    })
    refresh = res.cookies.get("refresh_token")

    # 2) Refresh
    res2 = client.post("/api/auth/refresh", json={
        "refresh_token": refresh
    })
    assert res2.status_code == 200

    data = res2.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["device_id"] == "pc-1"

    # check rotation : old token hash must be gone
    store = load_json(REFRESH_TOKENS_FILE)
    assert _token_hash(refresh) not in store


def test_refresh_unknown_token(create_user):
    create_user()

    res = client.post("/api/auth/refresh", json={
        "refresh_token": "invalid.refresh.token"
    })

    assert res.status_code == 401


# ----------------------------------------------------------------------
# TEST LOGOUT
# ----------------------------------------------------------------------
def test_logout(create_user):
    create_user()

    res = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
        "device_id": "pc-1"
    })
    refresh = res.cookies.get("refresh_token")

    res2 = client.post("/api/auth/logout", json={
        "refresh_token": refresh
    })
    assert res2.status_code == 200

    store = load_json(REFRESH_TOKENS_FILE)
    assert _token_hash(refresh) not in store


# ----------------------------------------------------------------------
# TEST LOGOUT ALL
# ----------------------------------------------------------------------
def test_logout_all(create_user):
    uid = create_user()

    # login on 2 devices
    t1 = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
        "device_id": "pc1"
    }).cookies.get("refresh_token")

    t2 = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
        "device_id": "pc2"
    }).cookies.get("refresh_token")

    # logout_all requires auth → call login to get access token
    login = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
    }).json()

    access = login["access_token"]

    res = client.post("/api/auth/logout_all",
                      headers={"Authorization": f"Bearer {access}"})
    assert res.status_code == 200

    store = load_json(REFRESH_TOKENS_FILE)
    assert len(store) == 0


# ----------------------------------------------------------------------
# DEVICES LIST
# ----------------------------------------------------------------------
def test_list_devices(create_user):
    create_user()

    login = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
    }).json()

    access = login["access_token"]
    res = client.get("/api/auth/me/devices",
                     headers={"Authorization": f"Bearer {access}"})

    assert res.status_code == 200
    devices = res.json()["devices"]
    assert len(devices) == 1


# ----------------------------------------------------------------------
# DEVICE REVOKE
# ----------------------------------------------------------------------
def test_revoke_specific_device(create_user):
    create_user()

    # login on two devices
    res1 = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
        "device_id": "laptop"
    })
    t1 = res1.cookies.get("refresh_token")

    res2 = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
        "device_id": "mobile"
    })
    t2 = res2.cookies.get("refresh_token")

    # need access token for auth
    access = client.post("/api/auth/login", json={
        "login": "test",
        "password": "pass123",
    }).json()["access_token"]

    # Revoke laptop
    res = client.post(
        "/api/auth/me/devices/laptop/revoke",
        headers={"Authorization": f"Bearer {access}"}
    )
    assert res.status_code == 200

    store = load_json(REFRESH_TOKENS_FILE)
    token_hashes = set(store.keys())

    assert _token_hash(t1) not in token_hashes  # laptop revoked
    assert _token_hash(t2) in token_hashes      # mobile remains
