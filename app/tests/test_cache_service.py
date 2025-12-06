# app/tests/test_cache_service.py
"""
B-CraftD v3.0 - Tests Redis Cache Service
Date: 4 décembre 2025

Tests unitaires et d'intégration pour CacheService
"""

import pytest
import time
from services.cache_service import CacheService


@pytest.fixture(scope="module")
def cache_service():
    """Fixture pour initialiser le service de cache"""
    service = CacheService(
        host="localhost",
        port=6379,
        password="redis_secure_pass",
        db=1  # DB 1 pour les tests (séparé de prod)
    )
    yield service
    
    # Cleanup après tous les tests
    service.flush_all()
    service.close()


# =============================================================================
# TESTS UTILITAIRES GÉNÉRIQUES
# =============================================================================

def test_set_and_get(cache_service):
    """Test set/get basique"""
    key = "test:basic"
    value = {"name": "Test", "value": 123}
    
    assert cache_service.set(key, value)
    assert cache_service.get(key) == value


def test_get_nonexistent_key(cache_service):
    """Test récupération clé inexistante"""
    assert cache_service.get("nonexistent:key") is None


def test_set_with_ttl(cache_service):
    """Test expiration TTL"""
    key = "test:ttl"
    value = "expires_soon"
    
    cache_service.set(key, value, ttl=1)  # 1 seconde
    assert cache_service.get(key) == value
    
    time.sleep(1.5)
    assert cache_service.get(key) is None


def test_delete_keys(cache_service):
    """Test suppression de clés"""
    keys = ["test:del:1", "test:del:2", "test:del:3"]
    
    for key in keys:
        cache_service.set(key, "value")
    
    deleted = cache_service.delete(*keys)
    assert deleted == 3
    
    for key in keys:
        assert cache_service.get(key) is None


def test_exists(cache_service):
    """Test vérification existence"""
    key1 = "test:exists:1"
    key2 = "test:exists:2"
    key3 = "test:exists:missing"
    
    cache_service.set(key1, "value1")
    cache_service.set(key2, "value2")
    
    assert cache_service.exists(key1) == 1
    assert cache_service.exists(key1, key2) == 2
    assert cache_service.exists(key3) == 0


def test_expire(cache_service):
    """Test définition expiration"""
    key = "test:expire"
    cache_service.set(key, "value")
    
    assert cache_service.expire(key, 1)
    assert cache_service.get(key) == "value"
    
    time.sleep(1.5)
    assert cache_service.get(key) is None


def test_increment_decrement(cache_service):
    """Test incrémentation/décrémentation"""
    key = "test:counter"
    
    # Incrément
    assert cache_service.increment(key) == 1
    assert cache_service.increment(key, 5) == 6
    
    # Décrément
    assert cache_service.decrement(key, 2) == 4
    assert cache_service.decrement(key) == 3


# =============================================================================
# TESTS ENVIRONNEMENT
# =============================================================================

def test_current_environment(cache_service):
    """Test cache environnement complet"""
    environment = {
        "weather": {"name": "Ensoleillé", "multiplier": 1.0},
        "season": {"name": "Été", "multiplier": 1.0},
        "timestamp": "2025-12-04T10:00:00Z"
    }
    
    assert cache_service.set_current_environment(environment)
    assert cache_service.get_current_environment() == environment


def test_current_weather(cache_service):
    """Test cache météo actuelle"""
    weather = {
        "id": 1,
        "name": "Pluvieux",
        "gathering_multiplier": 0.8,
        "crafting_multiplier": 1.2
    }
    
    assert cache_service.set_current_weather(weather)
    assert cache_service.get_current_weather() == weather


def test_current_season(cache_service):
    """Test cache saison actuelle"""
    season = {
        "id": 2,
        "name": "Printemps",
        "gathering_multiplier": 1.2,
        "crafting_multiplier": 1.0
    }
    
    assert cache_service.set_current_season(season)
    assert cache_service.get_current_season() == season


def test_invalidate_environment(cache_service):
    """Test invalidation cache environnement"""
    cache_service.set_current_weather({"name": "Test"})
    cache_service.set_current_season({"name": "Test"})
    cache_service.set_current_environment({"test": "data"})
    
    deleted = cache_service.invalidate_environment()
    assert deleted >= 3
    
    assert cache_service.get_current_weather() is None
    assert cache_service.get_current_season() is None
    assert cache_service.get_current_environment() is None


# =============================================================================
# TESTS MARCHÉ
# =============================================================================

def test_market_listings_all(cache_service):
    """Test cache listings marché (tous)"""
    listings = [
        {"id": 1, "resource_id": 10, "price": 100.0},
        {"id": 2, "resource_id": 20, "price": 50.0}
    ]
    
    assert cache_service.set_market_listings(listings)
    assert cache_service.get_market_listings() == listings


def test_market_listings_by_resource(cache_service):
    """Test cache listings par ressource"""
    listings = [
        {"id": 1, "resource_id": 10, "price": 100.0},
        {"id": 2, "resource_id": 10, "price": 95.0}
    ]
    
    assert cache_service.set_market_listings(listings, resource_id=10)
    assert cache_service.get_market_listings(resource_id=10) == listings
    assert cache_service.get_market_listings(resource_id=99) is None


def test_invalidate_market_cache_specific(cache_service):
    """Test invalidation marché ressource spécifique"""
    cache_service.set_market_listings([{"id": 1}], resource_id=10)
    cache_service.set_market_listings([{"id": 2}], resource_id=20)
    
    deleted = cache_service.invalidate_market_cache(resource_id=10)
    assert deleted >= 1
    
    assert cache_service.get_market_listings(resource_id=10) is None
    assert cache_service.get_market_listings(resource_id=20) is not None


def test_invalidate_market_cache_all(cache_service):
    """Test invalidation tout le marché"""
    cache_service.set_market_listings([{"id": 1}], resource_id=10)
    cache_service.set_market_listings([{"id": 2}], resource_id=20)
    
    deleted = cache_service.invalidate_market_cache()
    assert deleted >= 2
    
    assert cache_service.get_market_listings(resource_id=10) is None
    assert cache_service.get_market_listings(resource_id=20) is None


# =============================================================================
# TESTS LEADERBOARD
# =============================================================================

def test_leaderboard(cache_service):
    """Test cache leaderboard"""
    leaderboard = [
        {"rank": 1, "user": "player1", "score": 10000},
        {"rank": 2, "user": "player2", "score": 9500},
        {"rank": 3, "user": "player3", "score": 9000}
    ]
    
    assert cache_service.set_leaderboard(leaderboard, limit=100)
    assert cache_service.get_leaderboard(limit=100) == leaderboard


def test_invalidate_leaderboard(cache_service):
    """Test invalidation leaderboard"""
    cache_service.set_leaderboard([{"rank": 1}], limit=100)
    cache_service.set_leaderboard([{"rank": 1}], limit=50)
    
    deleted = cache_service.invalidate_leaderboard()
    assert deleted >= 2
    
    assert cache_service.get_leaderboard(limit=100) is None


# =============================================================================
# TESTS INVENTAIRE
# =============================================================================

def test_user_inventory(cache_service):
    """Test cache inventaire utilisateur"""
    user_id = 123
    inventory = [
        {"resource_id": 1, "quantity": 50},
        {"resource_id": 2, "quantity": 25}
    ]
    
    assert cache_service.set_user_inventory(user_id, inventory)
    assert cache_service.get_user_inventory(user_id) == inventory


def test_invalidate_user_inventory(cache_service):
    """Test invalidation inventaire utilisateur"""
    user_id = 456
    cache_service.set_user_inventory(user_id, [{"resource_id": 1}])
    
    deleted = cache_service.invalidate_user_inventory(user_id)
    assert deleted == 1
    assert cache_service.get_user_inventory(user_id) is None


# =============================================================================
# TESTS RECETTES
# =============================================================================

def test_craftable_recipes(cache_service):
    """Test cache recettes craftables"""
    user_id = 789
    profession_id = 1
    recipes = [
        {"id": 1, "name": "Épée en Fer", "can_craft": True},
        {"id": 2, "name": "Bouclier", "can_craft": False}
    ]
    
    assert cache_service.set_craftable_recipes(user_id, profession_id, recipes)
    assert cache_service.get_craftable_recipes(user_id, profession_id) == recipes


def test_invalidate_user_recipes(cache_service):
    """Test invalidation recettes utilisateur"""
    user_id = 999
    cache_service.set_craftable_recipes(user_id, 1, [{"id": 1}])
    cache_service.set_craftable_recipes(user_id, 2, [{"id": 2}])
    
    deleted = cache_service.invalidate_user_recipes(user_id)
    assert deleted >= 2
    
    assert cache_service.get_craftable_recipes(user_id, 1) is None
    assert cache_service.get_craftable_recipes(user_id, 2) is None


# =============================================================================
# TESTS SESSIONS
# =============================================================================

def test_session_lifecycle(cache_service):
    """Test cycle de vie session"""
    session_id = "session_abc123"
    user_data = {"user_id": 1, "login": "player1", "role": "player"}
    
    # Créer session
    assert cache_service.set_session(session_id, user_data)
    
    # Récupérer session
    assert cache_service.get_session(session_id) == user_data
    
    # Refresh session
    assert cache_service.refresh_session(session_id)
    
    # Supprimer session
    assert cache_service.delete_session(session_id) == 1
    assert cache_service.get_session(session_id) is None


# =============================================================================
# TESTS RATE LIMITING
# =============================================================================

def test_rate_limit_basic(cache_service):
    """Test rate limiting basique"""
    identifier = "user_ratelimit_1"
    max_requests = 3
    window = 60
    
    # 3 premières requêtes OK
    for _ in range(max_requests):
        assert cache_service.check_rate_limit(identifier, max_requests, window)
    
    # 4ème requête bloquée
    assert not cache_service.check_rate_limit(identifier, max_requests, window)


def test_rate_limit_remaining(cache_service):
    """Test compteur requêtes restantes"""
    identifier = "user_ratelimit_2"
    max_requests = 5
    
    # Vérifier requêtes restantes
    assert cache_service.get_remaining_requests(identifier, max_requests) == 5
    
    # Consommer 2 requêtes
    cache_service.check_rate_limit(identifier, max_requests, 60)
    cache_service.check_rate_limit(identifier, max_requests, 60)
    
    assert cache_service.get_remaining_requests(identifier, max_requests) == 3


def test_rate_limit_window_reset(cache_service):
    """Test reset fenêtre rate limit"""
    identifier = "user_ratelimit_3"
    max_requests = 2
    window = 1  # 1 seconde
    
    # Consommer les 2 requêtes
    assert cache_service.check_rate_limit(identifier, max_requests, window)
    assert cache_service.check_rate_limit(identifier, max_requests, window)
    assert not cache_service.check_rate_limit(identifier, max_requests, window)
    
    # Attendre reset
    time.sleep(1.5)
    
    # Nouvelle fenêtre
    assert cache_service.check_rate_limit(identifier, max_requests, window)


# =============================================================================
# TESTS STATISTIQUES
# =============================================================================

def test_get_stats(cache_service):
    """Test récupération statistiques Redis"""
    stats = cache_service.get_stats()
    
    assert "connected_clients" in stats
    assert "used_memory_human" in stats
    assert "hit_rate" in stats
    assert "redis_version" in stats
    assert isinstance(stats["hit_rate"], float)


def test_hit_rate_calculation(cache_service):
    """Test calcul hit rate"""
    # Générer hits
    cache_service.set("test:hit:1", "value")
    cache_service.get("test:hit:1")  # HIT
    cache_service.get("test:hit:1")  # HIT
    
    # Générer miss
    cache_service.get("test:hit:nonexistent")  # MISS
    
    stats = cache_service.get_stats()
    assert stats["hit_rate"] >= 0
    assert stats["hit_rate"] <= 100


# =============================================================================
# TESTS D'INTÉGRATION
# =============================================================================

def test_full_workflow_environment():
    """Test workflow complet environnement"""
    cache = CacheService(host="localhost", port=6379, password="redis_secure_pass", db=1)
    
    # 1. Cacher météo et saison
    cache.set_current_weather({"name": "Ensoleillé", "multiplier": 1.0})
    cache.set_current_season({"name": "Été", "multiplier": 1.0})
    
    # 2. Vérifier cache
    assert cache.get_current_weather()["name"] == "Ensoleillé"
    assert cache.get_current_season()["name"] == "Été"
    
    # 3. Invalider tout
    cache.invalidate_environment()
    
    # 4. Vérifier invalidation
    assert cache.get_current_weather() is None
    assert cache.get_current_season() is None
    
    cache.close()


def test_full_workflow_market():
    """Test workflow complet marché"""
    cache = CacheService(host="localhost", port=6379, password="redis_secure_pass", db=1)
    
    # 1. Utilisateur consulte marché
    listings = cache.get_market_listings(resource_id=10)
    assert listings is None  # Cache MISS
    
    # 2. Charger depuis DB et cacher
    db_listings = [{"id": 1, "price": 100.0}, {"id": 2, "price": 95.0}]
    cache.set_market_listings(db_listings, resource_id=10)
    
    # 3. Consultation suivante = cache HIT
    cached_listings = cache.get_market_listings(resource_id=10)
    assert cached_listings == db_listings
    
    # 4. Nouvelle vente = invalider cache
    cache.invalidate_market_cache(resource_id=10)
    assert cache.get_market_listings(resource_id=10) is None
    
    cache.close()


def test_full_workflow_rate_limiting():
    """Test workflow complet rate limiting API"""
    cache = CacheService(host="localhost", port=6379, password="redis_secure_pass", db=1)
    
    user_id = "api_user_999"
    max_requests = 10
    window = 60
    
    # Simuler appels API
    successful_requests = 0
    blocked_requests = 0
    
    for _ in range(15):
        if cache.check_rate_limit(user_id, max_requests, window):
            successful_requests += 1
        else:
            blocked_requests += 1
    
    assert successful_requests == 10
    assert blocked_requests == 5
    assert cache.get_remaining_requests(user_id, max_requests) == 0
    
    cache.close()


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])