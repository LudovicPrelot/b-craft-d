# tests/test_users.py

def test_me_requires_login(client):
    r = client.get("/me")
    assert r.status_code == 401

def test_admin_can_list_users(client):
    # Login as admin
    r = client.post("/auth/login", json={"login": "admin", "password": "admin"})
    token = r.json()["access_token"]

    r = client.get("/users", headers={"Authorization": "Bearer "+token})
    assert r.status_code == 200
