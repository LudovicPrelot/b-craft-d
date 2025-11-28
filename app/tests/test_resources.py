# tests/test_resources.py

def test_resources_crud(client):
    login = client.post("/auth/login", json={"login": "admin", "password": "admin"})
    token = login.json()["access_token"]

    r = client.post("/resources/", json={"id": "argile", "name": "Argile"},
                    headers={"Authorization":"Bearer "+token})
    assert r.status_code == 200

    r = client.get("/resources/", headers={"Authorization":"Bearer "+token})
    assert r.status_code == 200

    r = client.delete("/resources/argile", headers={"Authorization":"Bearer "+token})
    assert r.status_code == 200
