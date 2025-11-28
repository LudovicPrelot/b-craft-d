# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from main import app
import uuid
import json
import config

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture
def admin_user():
    return {
        "id": str(uuid.uuid4()),
        "firstname": "Admin",
        "lastname": "Test",
        "mail": "admin@test.com",
        "login": "admin",
        "password_hash": "",
        "profession": "",
        "subclasses": [],
        "is_admin": True,
        "is_moderator": False,
    }

@pytest.fixture
def moderator_user():
    return {
        "id": str(uuid.uuid4()),
        "firstname": "Mod",
        "lastname": "Test",
        "mail": "mod@test.com",
        "login": "mod",
        "password_hash": "",
        "profession": "",
        "subclasses": [],
        "is_admin": False,
        "is_moderator": True,
    }

@pytest.fixture
def player_user():
    return {
        "id": str(uuid.uuid4()),
        "firstname": "Player",
        "lastname": "Test",
        "mail": "player@test.com",
        "login": "player",
        "password_hash": "",
        "profession": "",
        "subclasses": [],
        "is_admin": False,
        "is_moderator": False,
    }
