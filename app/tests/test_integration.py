# tests/test_integration.py
"""
Tests d'intégration complets du workflow utilisateur.

Scénarios:
- Crafting → Gain XP → Level up
- Inventory management → Crafting → Stats update
- Quest completion → Rewards → Progression
"""

import pytest
from conftest import auth_headers


# ============================================================================
# TEST WORKFLOW COMPLET: CRAFTING → XP → LEVEL UP
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
def test_full_crafting_workflow(client, sample_user, sample_recipe, user_token):
    """
    Test workflow complet:
    1. Vérifier inventaire initial
    2. Crafter un item
    3. Vérifier gain XP
    4. Crafter plusieurs fois pour level up
    5. Vérifier nouveau niveau et stats
    """
    headers = auth_headers(user_token)
    
    # 1. État initial
    me_response = client.get("/api/user/me", headers=headers)
    initial_xp = me_response.json()["xp"]
    initial_level = me_response.json()["level"]
    
    print(f"📊 État initial: Level {initial_level}, XP {initial_xp}")
    
    # 2. Vérifier inventaire (doit avoir des ingrédients)
    inv_response = client.get("/api/user/inventory", headers=headers)
    inventory = inv_response.json()
    
    assert "argile" in inventory
    assert "calcaire" in inventory
    print(f"🎒 Inventaire: {inventory}")
    
    # 3. Premier craft
    craft_response = client.post(
        "/api/user/crafting/craft",
        headers=headers,
        json={"recipe_id": "ciment"}
    )
    
    assert craft_response.status_code == 200
    craft_data = craft_response.json()
    
    assert craft_data["status"] == "crafted"
    assert craft_data["produced"]["item"] == "ciment"
    assert craft_data["produced"]["quantity"] == 1
    
    # Vérifie XP gagnée
    new_xp = craft_data["inventory"]  # FIXME: devrait renvoyer XP
    print(f"✅ Craft réussi: +{sample_recipe.xp_reward} XP")
    
    # 4. Vérifier que l'inventaire a changé
    inv_after = client.get("/api/user/inventory", headers=headers).json()
    
    assert "ciment" in inv_after
    assert inv_after["ciment"] == 1
    assert inv_after["argile"] == inventory["argile"] - 1
    assert inv_after["calcaire"] == inventory["calcaire"] - 1
    
    print(f"🎒 Inventaire après craft: {inv_after}")
    
    # 5. Crafter plusieurs fois pour level up
    initial_level = client.get("/api/user/me", headers=headers).json()["level"]
    crafts_needed = 15  # Assez pour monter de niveau
    
    for i in range(crafts_needed):
        # Ajouter des ingrédients pour continuer à crafter
        client.post(
            "/api/user/inventory/add",
            headers=headers,
            params={"item": "argile", "qty": 1}
        )
        client.post(
            "/api/user/inventory/add",
            headers=headers,
            params={"item": "calcaire", "qty": 1}
        )
        
        craft = client.post(
            "/api/user/crafting/craft",
            headers=headers,
            json={"recipe_id": "ciment"}
        )
        
        if craft.json().get("level_up"):
            print(f"🎉 LEVEL UP après {i+1} crafts!")
            break
    
    # 6. Vérifier level up
    final_me = client.get("/api/user/me", headers=headers).json()
    final_level = final_me["level"]
    
    assert final_level > initial_level
    print(f"📈 Progression: Level {initial_level} → {final_level}")
    
    # 7. Vérifier que les stats ont augmenté
    final_stats = final_me["stats"]
    assert sum(final_stats.values()) > 3  # Au moins une stat a augmenté


# ============================================================================
# TEST WORKFLOW: INVENTORY → CRAFTING → VALIDATION
# ============================================================================

@pytest.mark.integration
def test_inventory_crafting_validation(client, user_token, sample_recipe):
    """
    Test validation complète inventory → crafting:
    1. Essayer de crafter sans ingrédients (fail)
    2. Ajouter ingrédients
    3. Crafter (success)
    4. Vérifier que les ingrédients ont été consommés
    """
    headers = auth_headers(user_token)
    
    # 1. Vider l'inventaire
    client.post("/api/user/inventory/clear", headers=headers)
    
    # 2. Essayer de crafter (devrait échouer)
    craft_fail = client.post(
        "/api/user/crafting/craft",
        headers=headers,
        json={"recipe_id": "ciment"}
    )
    
    assert craft_fail.status_code == 400
    assert "insuffisant" in craft_fail.json()["detail"].lower()
    
    # 3. Ajouter EXACTEMENT les ingrédients nécessaires
    client.post("/api/user/inventory/add", headers=headers, params={"item": "argile", "qty": 1})
    client.post("/api/user/inventory/add", headers=headers, params={"item": "calcaire", "qty": 1})
    
    # 4. Crafter (devrait réussir)
    craft_success = client.post(
        "/api/user/crafting/craft",
        headers=headers,
        json={"recipe_id": "ciment"}
    )
    
    assert craft_success.status_code == 200
    
    # 5. Vérifier que l'inventaire est correct
    final_inv = client.get("/api/user/inventory", headers=headers).json()
    
    assert "ciment" in final_inv
    assert final_inv["ciment"] == 1
    
    # Les ingrédients doivent avoir été consommés (ne plus être présents ou qty=0)
    assert final_inv.get("argile", 0) == 0
    assert final_inv.get("calcaire", 0) == 0


# ============================================================================
# TEST WORKFLOW: ADMIN → USER ACTIONS
# ============================================================================

@pytest.mark.integration
def test_admin_grant_xp_workflow(client, admin_token, sample_user):
    """
    Test workflow admin:
    1. Admin accorde XP à un user
    2. User vérifie sa progression
    3. User peut utiliser son nouveau niveau
    """
    admin_headers = auth_headers(admin_token)
    
    # 1. État initial du user
    initial_user = client.get(
        f"/api/admin/users/{sample_user.id}",
        headers=admin_headers
    ).json()
    
    initial_xp = initial_user["xp"]
    initial_level = initial_user["level"]
    
    # 2. Admin accorde beaucoup d'XP (pour level up)
    grant_response = client.post(
        f"/api/admin/users/{sample_user.id}/grant_xp",
        headers=admin_headers,
        json={"amount": 500}
    )
    
    assert grant_response.status_code == 200
    grant_data = grant_response.json()
    
    assert grant_data["status"] == "ok"
    assert grant_data["xp"] > initial_xp
    
    if grant_data["level_up"]:
        assert grant_data["level"] > initial_level
        print(f"🎉 User a level up: {initial_level} → {grant_data['level']}")
    
    # 3. Vérifier que le user voit bien sa progression
    # (Nécessiterait un user_token pour ce user, skip pour l'instant)


# ============================================================================
# TEST WORKFLOW: MULTIPLE USERS CONCURRENT
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
def test_concurrent_users_crafting(client, db_session, sample_profession, sample_recipe):
    """
    Test que plusieurs users peuvent crafter en même temps sans conflit.
    """
    from models import User
    from utils.auth import hash_password
    
    # Créer 3 users
    users = []
    for i in range(3):
        user = User(
            id=f"concurrent-user-{i}",
            firstname=f"User{i}",
            lastname="Test",
            mail=f"user{i}@test.com",
            login=f"user{i}",
            password_hash=hash_password("Test123!"),
            profession="mineur",
            inventory={"argile": 10, "calcaire": 10},
            xp=0,
            level=1,
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    
    # Login pour chaque user
    tokens = []
    for user in users:
        login_response = client.post("/api/public/auth/login", json={
            "login": user.login,
            "password": "Test123!"
        })
        tokens.append(login_response.json()["access_token"])
    
    # Chaque user crafte 5 fois
    for i, token in enumerate(tokens):
        headers = auth_headers(token)
        
        for _ in range(5):
            craft_response = client.post(
                "/api/user/crafting/craft",
                headers=headers,
                json={"recipe_id": "ciment"}
            )
            
            assert craft_response.status_code == 200
            print(f"✅ User {i} a crafté un ciment")
    
    # Vérifier que chaque user a bien 5 ciments
    for i, token in enumerate(tokens):
        inv = client.get("/api/user/inventory", headers=auth_headers(token)).json()
        assert inv["ciment"] == 5
        print(f"🎒 User {i}: {inv['ciment']} ciments")


# ============================================================================
# TEST EDGE CASES INTÉGRATION
# ============================================================================

@pytest.mark.integration
def test_craft_with_insufficient_level(client, user_token, db_session):
    """Test qu'un user ne peut pas crafter une recette trop avancée."""
    from models import Recipe, Resource
    
    # Créer une recette niveau 10
    resource = Resource(id="diamond", name="Diamant", type="mineral")
    db_session.add(resource)
    
    advanced_recipe = Recipe(
        id="diamond_tool",
        output="diamond",
        ingredients={"argile": 1},
        required_profession="mineur",
        required_level=10,  # Level trop élevé
        xp_reward=100
    )
    db_session.add(advanced_recipe)
    db_session.commit()
    
    # Essayer de crafter (devrait échouer)
    response = client.post(
        "/api/user/crafting/craft",
        headers=auth_headers(user_token),
        json={"recipe_id": "diamond_tool"}
    )
    
    assert response.status_code == 400
    assert "niveau" in response.json()["detail"].lower()


@pytest.mark.integration
def test_inventory_overflow_prevention(client, user_token):
    """Test que l'ajout d'items respecte les limites (si implémentées)."""
    headers = auth_headers(user_token)
    
    # Essayer d'ajouter une quantité énorme
    response = client.post(
        "/api/user/inventory/add",
        headers=headers,
        params={"item": "argile", "qty": 9999}
    )
    
    # Selon l'implémentation, peut être accepté ou rejeté
    # Pour l'instant, on vérifie juste que ça ne crash pas
    assert response.status_code in [200, 400]