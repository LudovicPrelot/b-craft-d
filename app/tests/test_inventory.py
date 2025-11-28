import pytest
from fastapi.testclient import TestClient
from main import app
import json, uuid
import config
from utils.storage import save_json

client = TestClient(app)

@pytest.fixture
def token_user():
    # reset storage
    save_json(config.USERS_FILE, {})

    # register user
    r = client.post("/auth/register", json={
        "firstname": "Test",
        "lastname": "User",
        "mail": "t@t.com",
        "login": "testu",
        "password": "pwd",
        "profession": "miner",
        "subclasses": []
    })
    assert r.status_code == 200

    # login
    r = client.post("/auth/login", json={"login": "testu", "password": "pwd"})
    assert r.status_code == 200
    return r.json()["access_token"]

def headers(token):
    return {"Authorization": f"Bearer {token}"}

def test_add_inventory(token_user):
    r = client.post("/inventory/add?item=argile&qty=3", headers=headers(token_user))
    assert r.status_code == 200
    assert r.json()["inventory"]["argile"] == 3

def test_remove_inventory(token_user):
    # add
    client.post("/inventory/add?item=argile&qty=5", headers=headers(token_user))
    # remove
    r = client.post("/inventory/remove?item=argile&qty=2", headers=headers(token_user))
    assert r.status_code == 200
    assert r.json()["inventory"]["argile"] == 3

def test_clear_inventory(token_user):
    client.post("/inventory/add?item=calcaire&qty=10", headers=headers(token_user))
    r = client.post("/inventory/clear", headers=headers(token_user))
    assert r.status_code == 200
    assert r.json()["status"] == "cleared"
