import pytest
from fastapi.testclient import TestClient
from utils.json import save_json
import config
from main import app

client = TestClient(app)

@pytest.fixture
def setup_env():
    save_json(config.USERS_FILE, {})
    save_json(config.RECIPES_FILE, {
        "ciment": {
            "id": "ciment",
            "required_profession": "miner",
            "ingredients": {
                "argile": 2,
                "calcaire": 1
            },
            "output": "ciment"
        }
    })
    return True

@pytest.fixture
def token_user(setup_env):
    client.post("/auth/register", json={
        "firstname": "Craft",
        "lastname": "User",
        "mail": "craft@t.com",
        "login": "craft",
        "password": "pwd",
        "profession": "miner",
        "subclasses": []
    })
    r = client.post("/auth/login", json={"login": "craft", "password": "pwd"})
    return r.json()["access_token"]

def h(token): return {"Authorization": f"Bearer {token}"}

def test_possible_recipes(token_user):
    # add ingredients
    client.post("/inventory/add?item=argile&qty=2", headers=h(token_user))
    client.post("/inventory/add?item=calcaire&qty=1", headers=h(token_user))

    r = client.get("/crafting/possible", headers=h(token_user))
    assert r.status_code == 200
    j = r.json()
    assert len(j) == 1
    assert j[0]["id"] == "ciment"

def test_craft_ok(token_user):
    client.post("/inventory/add?item=argile&qty=2", headers=h(token_user))
    client.post("/inventory/add?item=calcaire&qty=1", headers=h(token_user))

    r = client.post("/crafting/craft", json={"recipe_id": "ciment"}, headers=h(token_user))
    assert r.status_code == 200
    j = r.json()
    assert j["produced"]["output"] == "ciment"
    assert "ciment" in j["inventory"]
