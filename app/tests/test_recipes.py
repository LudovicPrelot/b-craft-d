# tests/test_recipes.py

def test_recipes_crud(client):
    login = client.post("/auth/login", json={"login": "admin", "password": "admin"})
    token = login.json()["access_token"]

    r = client.post("/recipes/", json={
        "id": "ciment",
        "output": "ciment",
        "required_profession": "mineur",
        "ingredients": {"argile": 2, "calcaire": 1}
    }, headers={"Authorization":"Bearer "+token})
    assert r.status_code == 200

    r = client.get("/recipes/", headers={"Authorization":"Bearer "+token})
    assert r.status_code == 200

    r = client.delete("/recipes/ciment", headers={"Authorization":"Bearer "+token})
    assert r.status_code == 200
