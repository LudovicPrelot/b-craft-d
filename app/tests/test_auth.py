# tests/test_auth.py

import json
import config

def test_register_and_login(client):
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "mail": "john@test.com",
        "login": "johndoe",
        "password": "123456",
        "profession": "mineur",
        "subclasses": []
    }

    r = client.post("/auth/register", json=payload)
    assert r.status_code == 200

    r = client.post("/auth/login", json={"login": "johndoe", "password": "123456"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
