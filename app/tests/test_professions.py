# tests/test_professions.py

def test_profession_crud_admin(client):
    login = client.post("/auth/login", json={"login": "admin", "password": "admin"})
    token = login.json()["access_token"]

    # Create
    r = client.post("/professions/", json={"id":"mineur","name":"Mineur","subclasses":[]},
                    headers={"Authorization": "Bearer "+token})
    assert r.status_code == 200

    # List
    r = client.get("/professions/", headers={"Authorization": "Bearer "+token})
    assert r.status_code == 200

    # Delete
    r = client.delete("/professions/mineur",
                      headers={"Authorization": "Bearer "+token})
    assert r.status_code == 200
