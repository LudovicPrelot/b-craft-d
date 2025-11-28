import pytest
from fastapi.testclient import TestClient
from main import app
from utils.storage import save_json
import config

client = TestClient(app)

@pytest.fixture
def token_user():
    save_json(config.USERS_FILE, {})

    client.post("/auth/register", json={
        "firstname": "Loot",
        "lastname": "User",
        "mail": "loot@t.com",
        "login": "loot",
        "password": "pwd",
        "profession": "miner",
        "subclasses": []
    })

    r = client.post("/auth/login", json={"login": "loot", "password": "pwd"})
    return r.json()["access_token"]

def test_loot_collect(token_user):
    r = client.post("/loot/collect", headers={"Authorization": f"Bearer {token_user}"})
    assert r.status_code == 200
    j = r.json()
    assert "gained" in j
    assert isinstance(j["gained"], dict)
    assert len(j["gained"]) >= 1
