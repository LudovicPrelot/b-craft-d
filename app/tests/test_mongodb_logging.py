"""
B-CraftD v3.0 - Tests MongoDB Logging Service
Date: 4 décembre 2025

Tests unitaires et d'intégration pour LoggingService
"""

import pytest
from datetime import datetime, timedelta
from services.logging_service import LoggingService
from config import MONGO_URL


@pytest.fixture(scope="module")
def logging_service():
    """Fixture pour initialiser le service de logging"""
    service = LoggingService()
    yield service
    
    # Cleanup après tous les tests
    service.db.audit_logs.delete_many({})
    service.db.crafting_history.delete_many({})
    service.db.market_transactions.delete_many({})
    service.db.user_metrics.delete_many({})
    service.db.chat_messages.delete_many({})
    service.close()


# =============================================================================
# TESTS AUDIT LOGS
# =============================================================================

def test_log_audit_insert(logging_service):
    """Test création audit log INSERT"""
    audit_id = logging_service.log_audit(
        user_id=1,
        action="INSERT",
        table_name="users",
        record_id=1,
        new_values={"login": "test_user", "email": "test@example.com"},
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0"
    )
    
    assert audit_id is not None
    assert len(audit_id) > 0


def test_log_audit_update(logging_service):
    """Test création audit log UPDATE"""
    audit_id = logging_service.log_audit(
        user_id=1,
        action="UPDATE",
        table_name="users",
        record_id=1,
        old_values={"coins": 100.0},
        new_values={"coins": 150.0},
        ip_address="192.168.1.1"
    )
    
    assert audit_id is not None


def test_get_user_audit_history(logging_service):
    """Test récupération historique audit"""
    # Créer 3 logs
    for i in range(3):
        logging_service.log_audit(
            user_id=2,
            action="INSERT",
            table_name=f"table_{i}",
            record_id=i
        )
    
    history = logging_service.get_user_audit_history(user_id=2, limit=10)
    assert len(history) >= 3
    assert history[0]["user_id"] == 2


def test_audit_action_filter(logging_service):
    """Test filtrage par action"""
    # Créer logs différents
    logging_service.log_audit(user_id=3, action="INSERT", table_name="test")
    logging_service.log_audit(user_id=3, action="UPDATE", table_name="test")
    logging_service.log_audit(user_id=3, action="DELETE", table_name="test")
    
    inserts = logging_service.get_user_audit_history(user_id=3, action_filter="INSERT")
    assert all(log["action"] == "INSERT" for log in inserts)


# =============================================================================
# TESTS CRAFTING HISTORY
# =============================================================================

def test_log_craft_success(logging_service):
    """Test enregistrement craft réussi"""
    craft_id = logging_service.log_craft(
        user_id=1,
        recipe_id=1,
        resource_id=10,
        quantity_crafted=5,
        ingredients_used=[
            {"resource_id": 1, "quantity": 10},
            {"resource_id": 2, "quantity": 5}
        ],
        profession_id=1,
        profession_level=25,
        experience_gained=50,
        success=True,
        crafting_time_seconds=120,
        weather_bonus=1.2,
        season_bonus=1.0,
        mastery_bonus=1.1
    )
    
    assert craft_id is not None


def test_log_craft_with_workshop(logging_service):
    """Test craft avec atelier"""
    craft_id = logging_service.log_craft(
        user_id=1,
        recipe_id=2,
        resource_id=20,
        quantity_crafted=1,
        ingredients_used=[{"resource_id": 5, "quantity": 20}],
        profession_id=2,
        profession_level=30,
        experience_gained=100,
        success=True,
        crafting_time_seconds=180,
        workshop_id=1,
        workshop_durability_before=100,
        workshop_durability_after=95
    )
    
    assert craft_id is not None


def test_get_user_craft_history(logging_service):
    """Test récupération historique craft"""
    # Créer crafts
    for i in range(5):
        logging_service.log_craft(
            user_id=4,
            recipe_id=i,
            resource_id=i+10,
            quantity_crafted=1,
            ingredients_used=[{"resource_id": 1, "quantity": 5}],
            profession_id=1,
            profession_level=20,
            experience_gained=10,
            success=(i % 2 == 0),  # Alternance succès/échec
            crafting_time_seconds=60
        )
    
    history = logging_service.get_user_craft_history(user_id=4, limit=10)
    assert len(history) == 5
    
    # Test filter success only
    success_only = logging_service.get_user_craft_history(user_id=4, success_only=True)
    assert all(craft["success"] for craft in success_only)
    assert len(success_only) == 3  # 3 sur 5 réussis


def test_recipe_success_rate(logging_service):
    """Test calcul taux de réussite recette"""
    # Créer 10 crafts: 7 succès, 3 échecs
    for i in range(10):
        logging_service.log_craft(
            user_id=5,
            recipe_id=100,
            resource_id=50,
            quantity_crafted=1,
            ingredients_used=[{"resource_id": 1, "quantity": 1}],
            profession_id=1,
            profession_level=15,
            experience_gained=5,
            success=(i < 7),  # 7 premiers = succès
            crafting_time_seconds=30
        )
    
    stats = logging_service.get_recipe_success_rate(recipe_id=100, days=30)
    assert stats["total_attempts"] == 10
    assert stats["successes"] == 7
    assert stats["failures"] == 3
    assert stats["success_rate"] == 70.0


# =============================================================================
# TESTS MARKET TRANSACTIONS
# =============================================================================

def test_log_market_transaction(logging_service):
    """Test enregistrement transaction marché"""
    transaction_id = logging_service.log_market_transaction(
        market_id=1,
        seller_id=1,
        buyer_id=2,
        resource_id=10,
        quantity=5,
        unit_price=100.50,
        total_price=502.50,
        seller_coins_before=1000.00,
        seller_coins_after=1502.50,
        buyer_coins_before=2000.00,
        buyer_coins_after=1497.50,
        listing_duration_hours=2.5,
        created_at=datetime.utcnow() - timedelta(hours=3),
        market_fee=5.0
    )
    
    assert transaction_id is not None


def test_market_analytics_all_resources(logging_service):
    """Test analytics marché toutes ressources"""
    # Créer plusieurs transactions
    for i in range(5):
        logging_service.log_market_transaction(
            market_id=i,
            seller_id=1,
            buyer_id=2,
            resource_id=i+10,
            quantity=i+1,
            unit_price=50.0 + (i * 10),
            total_price=(i+1) * (50.0 + (i * 10)),
            seller_coins_before=1000.0,
            seller_coins_after=1000.0 + ((i+1) * (50.0 + (i * 10))),
            buyer_coins_before=2000.0,
            buyer_coins_after=2000.0 - ((i+1) * (50.0 + (i * 10))),
            listing_duration_hours=1.0,
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
    
    analytics = logging_service.get_market_analytics(days=7)
    assert analytics["total_transactions"] == 5
    assert analytics["total_volume"] == 15  # 1+2+3+4+5
    assert analytics["avg_unit_price"] > 0


def test_market_analytics_specific_resource(logging_service):
    """Test analytics marché ressource spécifique"""
    # Créer transactions pour ressource 999
    for _ in range(3):
        logging_service.log_market_transaction(
            market_id=200,
            seller_id=1,
            buyer_id=2,
            resource_id=999,
            quantity=10,
            unit_price=75.0,
            total_price=750.0,
            seller_coins_before=1000.0,
            seller_coins_after=1750.0,
            buyer_coins_before=2000.0,
            buyer_coins_after=1250.0,
            listing_duration_hours=0.5,
            created_at=datetime.utcnow()
        )
    
    analytics = logging_service.get_market_analytics(resource_id=999, days=1)
    assert analytics["total_transactions"] == 3
    assert analytics["avg_unit_price"] == 75.0


# =============================================================================
# TESTS USER METRICS (Time-Series)
# =============================================================================

def test_log_user_metrics(logging_service):
    """Test enregistrement métriques utilisateur"""
    metrics_id = logging_service.log_user_metrics(
        user_id=1,
        level=15,
        experience=1500,
        coins=1502.50,
        active_professions=2,
        total_profession_levels=45,
        inventory_slots_used=23,
        inventory_total_value=5000.00,
        active_market_listings=3,
        crafts_last_hour=5,
        resources_gathered_last_hour=12,
        sales_last_hour=1,
        purchases_last_hour=0,
        online_status=True
    )
    
    assert metrics_id is not None


def test_user_progression_timeline(logging_service):
    """Test timeline progression utilisateur"""
    # Créer métriques horaires
    base_time = datetime.utcnow()
    for i in range(5):
        service = logging_service
        # Simuler progression temporelle (hack pour test)
        service.user_metrics.insert_one({
            "user_id": 6,
            "timestamp": base_time - timedelta(hours=i),
            "level": 10 + i,
            "experience": 1000 + (i * 100),
            "coins": 500.0 + (i * 50),
            "active_professions": 1,
            "total_profession_levels": 15 + (i * 2),
            "inventory_slots_used": 10 + i,
            "inventory_total_value": 1000.0,
            "active_market_listings": 0,
            "online_status": True
        })
    
    timeline = logging_service.get_user_progression_timeline(user_id=6, hours=24)
    assert len(timeline) == 5
    # Vérifier ordre chronologique
    for i in range(len(timeline) - 1):
        assert timeline[i]["timestamp"] <= timeline[i+1]["timestamp"]


# =============================================================================
# TESTS CHAT MESSAGES
# =============================================================================

def test_log_chat_message_global(logging_service):
    """Test message chat global"""
    msg_id = logging_service.log_chat_message(
        user_id=1,
        username="player1",
        message="Bonjour tout le monde !",
        channel="global"
    )
    
    assert msg_id is not None


def test_log_chat_message_whisper(logging_service):
    """Test message privé (whisper)"""
    msg_id = logging_service.log_chat_message(
        user_id=1,
        username="player1",
        message="Message privé",
        channel="whisper",
        recipient_id=2
    )
    
    assert msg_id is not None


def test_log_chat_message_guild(logging_service):
    """Test message guilde"""
    msg_id = logging_service.log_chat_message(
        user_id=1,
        username="player1",
        message="Réunion guilde ce soir",
        channel="guild",
        guild_id=10
    )
    
    assert msg_id is not None


def test_get_chat_history_global(logging_service):
    """Test récupération historique chat global"""
    # Créer messages
    for i in range(10):
        logging_service.log_chat_message(
            user_id=i,
            username=f"player{i}",
            message=f"Message {i}",
            channel="global"
        )
    
    history = logging_service.get_chat_history(channel="global", limit=10)
    assert len(history) >= 10
    assert all(msg["channel"] == "global" for msg in history)


def test_get_chat_history_guild(logging_service):
    """Test récupération historique chat guilde"""
    # Créer messages guilde spécifique
    guild_id = 50
    for i in range(5):
        logging_service.log_chat_message(
            user_id=1,
            username="guildmember",
            message=f"Guild message {i}",
            channel="guild",
            guild_id=guild_id
        )
    
    history = logging_service.get_chat_history(channel="guild", guild_id=guild_id, limit=10)
    assert len(history) == 5
    assert all(msg["guild_id"] == guild_id for msg in history)


def test_chat_message_truncation(logging_service):
    """Test troncature message >500 caractères"""
    long_message = "A" * 600  # 600 caractères
    
    msg_id = logging_service.log_chat_message(
        user_id=1,
        username="player1",
        message=long_message,
        channel="global"
    )
    
    # Vérifier que le message a été tronqué
    msg = logging_service.chat_messages.find_one({"_id": msg_id})
    assert len(msg["message"]) == 500


# =============================================================================
# TESTS UTILITAIRES
# =============================================================================

def test_get_collection_stats(logging_service):
    """Test statistiques collections"""
    stats = logging_service.get_collection_stats()
    
    assert "audit_logs" in stats
    assert "crafting_history" in stats
    assert "market_transactions" in stats
    assert "user_metrics" in stats
    assert "chat_messages" in stats
    
    # Vérifier structure
    for col, data in stats.items():
        assert "count" in data
        assert "size_mb" in data
        assert "avg_doc_size" in data
        assert "indexes" in data


def test_connection_close(logging_service):
    """Test fermeture connexion"""
    # Ce test ne doit pas lever d'exception
    logging_service.close()


# =============================================================================
# TESTS D'INTÉGRATION
# =============================================================================

def test_full_workflow_integration():
    """Test workflow complet: craft -> vente -> analytics"""
    service = LoggingService(db_name="bcraftd_test")
    
    # 1. Utilisateur crafte une ressource
    craft_id = service.log_craft(
        user_id=100,
        recipe_id=1,
        resource_id=50,
        quantity_crafted=10,
        ingredients_used=[{"resource_id": 1, "quantity": 20}],
        profession_id=1,
        profession_level=30,
        experience_gained=75,
        success=True,
        crafting_time_seconds=300
    )
    assert craft_id is not None
    
    # 2. Utilisateur vend la ressource
    transaction_id = service.log_market_transaction(
        market_id=500,
        seller_id=100,
        buyer_id=101,
        resource_id=50,
        quantity=10,
        unit_price=150.0,
        total_price=1500.0,
        seller_coins_before=500.0,
        seller_coins_after=2000.0,
        buyer_coins_before=5000.0,
        buyer_coins_after=3500.0,
        listing_duration_hours=1.5,
        created_at=datetime.utcnow() - timedelta(hours=2)
    )
    assert transaction_id is not None
    
    # 3. Enregistrer métriques
    metrics_id = service.log_user_metrics(
        user_id=100,
        level=30,
        experience=7500,
        coins=2000.0,
        active_professions=2,
        total_profession_levels=60,
        inventory_slots_used=15,
        inventory_total_value=3000.0,
        active_market_listings=0,
        crafts_last_hour=1,
        sales_last_hour=1
    )
    assert metrics_id is not None
    
    # 4. Vérifier analytics
    craft_history = service.get_user_craft_history(user_id=100, limit=1)
    assert len(craft_history) == 1
    assert craft_history[0]["resource_id"] == 50
    
    market_analytics = service.get_market_analytics(resource_id=50, days=1)
    assert market_analytics["total_transactions"] == 1
    assert market_analytics["total_value"] == 1500.0
    
    # Cleanup
    service.db.crafting_history.delete_many({"user_id": 100})
    service.db.market_transactions.delete_many({"seller_id": 100})
    service.db.user_metrics.delete_many({"user_id": 100})
    service.close()


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])