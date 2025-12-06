# app/services/logging_service.py
"""
B-CraftD v3.0 - MongoDB Logging Service
Date: 4 décembre 2025

Service pour logger les données vers MongoDB:
- Audit logs (CRUD operations)
- Crafting history
- Market transactions
- User metrics (time-series)
- Chat messages
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
import logging
from config import MONGO_URL

# Configuration logging Python standard
logger = logging.getLogger(__name__)


class LoggingService:
    """Service centralisé pour tous les logs MongoDB"""
    
    def __init__(self, mongo_uri: str = MONGO_URL, db_name: str = "bcraftd"):
        """
        Initialise la connexion MongoDB
        
        Args:
            mongo_uri: URI de connexion MongoDB
            db_name: Nom de la base de données
        """
        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            
            # Test de connexion
            self.client.server_info()
            logger.info(f"✅ Connexion MongoDB établie: {db_name}")
            
            # Références aux collections
            self.audit_logs: Collection = self.db.audit_logs
            self.crafting_history: Collection = self.db.crafting_history
            self.market_transactions: Collection = self.db.market_transactions
            self.user_metrics: Collection = self.db.user_metrics
            self.chat_messages: Collection = self.db.chat_messages
            
        except PyMongoError as e:
            logger.error(f"❌ Erreur connexion MongoDB: {e}")
            raise
    
    # =========================================================================
    # AUDIT LOGS
    # =========================================================================
    
    def log_audit(
        self,
        user_id: int,
        action: str,
        table_name: str,
        record_id: Optional[int] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Enregistre une action d'audit
        
        Args:
            user_id: ID de l'utilisateur
            action: Type d'action (INSERT, UPDATE, DELETE, SELECT)
            table_name: Nom de la table concernée
            record_id: ID de l'enregistrement modifié
            old_values: Valeurs avant modification (UPDATE/DELETE)
            new_values: Valeurs après modification (INSERT/UPDATE)
            ip_address: IP de l'utilisateur
            user_agent: User agent du navigateur
            
        Returns:
            str: ID du document créé
        """
        try:
            doc = {
                "user_id": user_id,
                "action": action,
                "table_name": table_name,
                "timestamp": datetime.utcnow()
            }
            
            if record_id is not None:
                doc["record_id"] = record_id
            if old_values:
                doc["old_values"] = old_values
            if new_values:
                doc["new_values"] = new_values
            if ip_address:
                doc["ip_address"] = ip_address
            if user_agent:
                doc["user_agent"] = user_agent
            
            result = self.audit_logs.insert_one(doc)
            logger.debug(f"Audit log créé: {action} sur {table_name} par user {user_id}")
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Erreur log_audit: {e}")
            raise
    
    def get_user_audit_history(
        self,
        user_id: int,
        limit: int = 100,
        action_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupère l'historique d'audit d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre max de résultats
            action_filter: Filtrer par type d'action (INSERT, UPDATE, etc.)
            
        Returns:
            List[Dict]: Liste des logs d'audit
        """
        try:
            query = {"user_id": user_id}
            if action_filter:
                query["action"] = action_filter
            
            cursor = self.audit_logs.find(query).sort("timestamp", DESCENDING).limit(limit)
            return list(cursor)
            
        except PyMongoError as e:
            logger.error(f"Erreur get_user_audit_history: {e}")
            return []
    
    # =========================================================================
    # CRAFTING HISTORY
    # =========================================================================
    
    def log_craft(
        self,
        user_id: int,
        recipe_id: int,
        resource_id: int,
        quantity_crafted: int,
        ingredients_used: List[Dict[str, int]],
        profession_id: int,
        profession_level: int,
        experience_gained: int,
        success: bool,
        crafting_time_seconds: int,
        weather_bonus: float = 1.0,
        season_bonus: float = 1.0,
        mastery_bonus: float = 1.0,
        workshop_id: Optional[int] = None,
        workshop_durability_before: Optional[int] = None,
        workshop_durability_after: Optional[int] = None
    ) -> str:
        """
        Enregistre un craft dans l'historique
        
        Args:
            user_id: ID de l'utilisateur
            recipe_id: ID de la recette
            resource_id: ID de la ressource produite
            quantity_crafted: Quantité craftée
            ingredients_used: Liste des ingrédients [{resource_id, quantity}]
            profession_id: ID de la profession
            profession_level: Niveau de la profession
            experience_gained: XP gagnée
            success: Craft réussi ou non
            crafting_time_seconds: Temps de craft
            weather_bonus: Multiplicateur météo
            season_bonus: Multiplicateur saison
            mastery_bonus: Multiplicateur maîtrise
            workshop_id: ID de l'atelier (optionnel)
            workshop_durability_before: Durabilité avant
            workshop_durability_after: Durabilité après
            
        Returns:
            str: ID du document créé
        """
        try:
            doc = {
                "user_id": user_id,
                "recipe_id": recipe_id,
                "resource_id": resource_id,
                "quantity_crafted": quantity_crafted,
                "ingredients_used": ingredients_used,
                "profession_id": profession_id,
                "profession_level": profession_level,
                "experience_gained": experience_gained,
                "success": success,
                "crafting_time_seconds": crafting_time_seconds,
                "weather_bonus": weather_bonus,
                "season_bonus": season_bonus,
                "mastery_bonus": mastery_bonus,
                "crafted_at": datetime.utcnow()
            }
            
            if workshop_id:
                doc["workshop_id"] = workshop_id
                doc["workshop_durability_before"] = workshop_durability_before
                doc["workshop_durability_after"] = workshop_durability_after
            
            result = self.crafting_history.insert_one(doc)
            logger.debug(f"Craft log créé: recipe {recipe_id} par user {user_id}")
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Erreur log_craft: {e}")
            raise
    
    def get_user_craft_history(
        self,
        user_id: int,
        limit: int = 50,
        success_only: bool = False
    ) -> List[Dict]:
        """
        Récupère l'historique de craft d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre max de résultats
            success_only: Uniquement les crafts réussis
            
        Returns:
            List[Dict]: Liste des crafts
        """
        try:
            query = {"user_id": user_id}
            if success_only:
                query["success"] = True
            
            cursor = self.crafting_history.find(query).sort("crafted_at", DESCENDING).limit(limit)
            return list(cursor)
            
        except PyMongoError as e:
            logger.error(f"Erreur get_user_craft_history: {e}")
            return []
    
    def get_recipe_success_rate(self, recipe_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Calcule le taux de réussite d'une recette
        
        Args:
            recipe_id: ID de la recette
            days: Période d'analyse (jours)
            
        Returns:
            Dict: {total_attempts, successes, failures, success_rate}
        """
        try:
            date_threshold = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {
                    "recipe_id": recipe_id,
                    "crafted_at": {"$gte": date_threshold}
                }},
                {"$group": {
                    "_id": None,
                    "total_attempts": {"$sum": 1},
                    "successes": {"$sum": {"$cond": ["$success", 1, 0]}},
                    "failures": {"$sum": {"$cond": ["$success", 0, 1]}}
                }}
            ]
            
            result = list(self.crafting_history.aggregate(pipeline))
            
            if result:
                data = result[0]
                data["success_rate"] = (data["successes"] / data["total_attempts"] * 100) if data["total_attempts"] > 0 else 0
                return data
            
            return {"total_attempts": 0, "successes": 0, "failures": 0, "success_rate": 0}
            
        except PyMongoError as e:
            logger.error(f"Erreur get_recipe_success_rate: {e}")
            return {"total_attempts": 0, "successes": 0, "failures": 0, "success_rate": 0}
    
    # =========================================================================
    # MARKET TRANSACTIONS
    # =========================================================================
    
    def log_market_transaction(
        self,
        market_id: int,
        seller_id: int,
        buyer_id: int,
        resource_id: int,
        quantity: int,
        unit_price: float,
        total_price: float,
        seller_coins_before: float,
        seller_coins_after: float,
        buyer_coins_before: float,
        buyer_coins_after: float,
        listing_duration_hours: float,
        created_at: datetime,
        market_fee: float = 0.0
    ) -> str:
        """
        Enregistre une transaction de marché
        
        Args:
            market_id: ID de l'offre marché
            seller_id: ID du vendeur
            buyer_id: ID de l'acheteur
            resource_id: ID de la ressource
            quantity: Quantité échangée
            unit_price: Prix unitaire
            total_price: Prix total
            seller_coins_before: Coins vendeur avant
            seller_coins_after: Coins vendeur après
            buyer_coins_before: Coins acheteur avant
            buyer_coins_after: Coins acheteur après
            listing_duration_hours: Durée de l'offre
            created_at: Date création offre
            market_fee: Frais de marché
            
        Returns:
            str: ID du document créé
        """
        try:
            doc = {
                "market_id": market_id,
                "seller_id": seller_id,
                "buyer_id": buyer_id,
                "resource_id": resource_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "seller_coins_before": seller_coins_before,
                "seller_coins_after": seller_coins_after,
                "buyer_coins_before": buyer_coins_before,
                "buyer_coins_after": buyer_coins_after,
                "listing_duration_hours": listing_duration_hours,
                "market_fee": market_fee,
                "transaction_date": datetime.utcnow(),
                "created_at": created_at
            }
            
            result = self.market_transactions.insert_one(doc)
            logger.debug(f"Transaction log créée: market {market_id}")
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Erreur log_market_transaction: {e}")
            raise
    
    def get_market_analytics(
        self,
        resource_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analytics du marché pour une ressource
        
        Args:
            resource_id: ID de la ressource (None = toutes)
            days: Période d'analyse
            
        Returns:
            Dict: Analytics (total_transactions, volume, avg_price, etc.)
        """
        try:
            date_threshold = datetime.utcnow() - timedelta(days=days)
            
            match_stage = {"transaction_date": {"$gte": date_threshold}}
            if resource_id:
                match_stage["resource_id"] = resource_id
            
            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": None,
                    "total_transactions": {"$sum": 1},
                    "total_volume": {"$sum": "$quantity"},
                    "total_value": {"$sum": "$total_price"},
                    "avg_unit_price": {"$avg": "$unit_price"},
                    "min_unit_price": {"$min": "$unit_price"},
                    "max_unit_price": {"$max": "$unit_price"},
                    "avg_listing_duration": {"$avg": "$listing_duration_hours"}
                }}
            ]
            
            result = list(self.market_transactions.aggregate(pipeline))
            return result[0] if result else {}
            
        except PyMongoError as e:
            logger.error(f"Erreur get_market_analytics: {e}")
            return {}
    
    # =========================================================================
    # USER METRICS (Time-Series)
    # =========================================================================
    
    def log_user_metrics(
        self,
        user_id: int,
        level: int,
        experience: int,
        coins: float,
        active_professions: int,
        total_profession_levels: int,
        inventory_slots_used: int,
        inventory_total_value: float,
        active_market_listings: int,
        crafts_last_hour: int = 0,
        resources_gathered_last_hour: int = 0,
        sales_last_hour: int = 0,
        purchases_last_hour: int = 0,
        online_status: bool = True
    ) -> str:
        """
        Enregistre les métriques utilisateur (snapshot horaire)
        
        Args:
            user_id: ID de l'utilisateur
            level: Niveau du personnage
            experience: XP du personnage
            coins: Monnaie
            active_professions: Nombre de professions actives
            total_profession_levels: Somme des niveaux professions
            inventory_slots_used: Slots inventaire utilisés
            inventory_total_value: Valeur totale inventaire
            active_market_listings: Nombre d'offres actives
            crafts_last_hour: Crafts dernière heure
            resources_gathered_last_hour: Ressources collectées
            sales_last_hour: Ventes dernière heure
            purchases_last_hour: Achats dernière heure
            online_status: Statut en ligne
            
        Returns:
            str: ID du document créé
        """
        try:
            doc = {
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "level": level,
                "experience": experience,
                "coins": coins,
                "active_professions": active_professions,
                "total_profession_levels": total_profession_levels,
                "inventory_slots_used": inventory_slots_used,
                "inventory_total_value": inventory_total_value,
                "active_market_listings": active_market_listings,
                "crafts_last_hour": crafts_last_hour,
                "resources_gathered_last_hour": resources_gathered_last_hour,
                "sales_last_hour": sales_last_hour,
                "purchases_last_hour": purchases_last_hour,
                "online_status": online_status
            }
            
            result = self.user_metrics.insert_one(doc)
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Erreur log_user_metrics: {e}")
            raise
    
    def get_user_progression_timeline(
        self,
        user_id: int,
        hours: int = 24
    ) -> List[Dict]:
        """
        Timeline de progression d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            hours: Période en heures
            
        Returns:
            List[Dict]: Métriques horaires
        """
        try:
            date_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            cursor = self.user_metrics.find({
                "user_id": user_id,
                "timestamp": {"$gte": date_threshold}
            }).sort("timestamp", ASCENDING)
            
            return list(cursor)
            
        except PyMongoError as e:
            logger.error(f"Erreur get_user_progression_timeline: {e}")
            return []
    
    # =========================================================================
    # CHAT MESSAGES
    # =========================================================================
    
    def log_chat_message(
        self,
        user_id: int,
        username: str,
        message: str,
        channel: str,
        recipient_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        is_system_message: bool = False
    ) -> str:
        """
        Enregistre un message de chat
        
        Args:
            user_id: ID de l'utilisateur
            username: Nom d'utilisateur
            message: Contenu du message
            channel: Canal (global, trade, profession, guild, whisper)
            recipient_id: ID destinataire (whisper)
            guild_id: ID guilde (chat guilde)
            is_system_message: Message système
            
        Returns:
            str: ID du document créé
        """
        try:
            doc = {
                "user_id": user_id,
                "username": username,
                "message": message[:500],  # Limite 500 caractères
                "channel": channel,
                "is_system_message": is_system_message,
                "sent_at": datetime.utcnow()
            }
            
            if recipient_id:
                doc["recipient_id"] = recipient_id
            if guild_id:
                doc["guild_id"] = guild_id
            
            result = self.chat_messages.insert_one(doc)
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Erreur log_chat_message: {e}")
            raise
    
    def get_chat_history(
        self,
        channel: str,
        limit: int = 100,
        guild_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Récupère l'historique d'un canal de chat
        
        Args:
            channel: Nom du canal
            limit: Nombre de messages
            guild_id: ID guilde (pour chat guilde)
            
        Returns:
            List[Dict]: Messages du canal
        """
        try:
            query = {"channel": channel}
            if guild_id:
                query["guild_id"] = guild_id
            
            cursor = self.chat_messages.find(query).sort("sent_at", DESCENDING).limit(limit)
            messages = list(cursor)
            messages.reverse()  # Ordre chronologique
            return messages
            
        except PyMongoError as e:
            logger.error(f"Erreur get_chat_history: {e}")
            return []
    
    # =========================================================================
    # UTILITAIRES
    # =========================================================================
    
    def get_collection_stats(self) -> Dict[str, Dict]:
        """
        Statistiques de toutes les collections
        
        Returns:
            Dict: Stats par collection
        """
        try:
            collections = [
                "audit_logs", "crafting_history", "market_transactions",
                "user_metrics", "chat_messages"
            ]
            
            stats = {}
            for col_name in collections:
                col = self.db[col_name]
                col_stats = col.stats()
                stats[col_name] = {
                    "count": col_stats.get("count", 0),
                    "size_mb": col_stats.get("size", 0) / (1024 * 1024),
                    "avg_doc_size": col_stats.get("avgObjSize", 0),
                    "indexes": col_stats.get("nindexes", 0)
                }
            
            return stats
            
        except PyMongoError as e:
            logger.error(f"Erreur get_collection_stats: {e}")
            return {}
    
    def close(self):
        """Ferme la connexion MongoDB"""
        self.client.close()
        logger.info("Connexion MongoDB fermée")


# =========================================================================
# EXEMPLE D'UTILISATION
# =========================================================================

if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialisation
    service = LoggingService()
    
    # Test audit log
    audit_id = service.log_audit(
        user_id=1,
        action="INSERT",
        table_name="users",
        new_values={"login": "test", "email": "test@example.com"},
        ip_address="127.0.0.1"
    )
    print(f"✅ Audit log créé: {audit_id}")
    
    # Test craft log
    craft_id = service.log_craft(
        user_id=1,
        recipe_id=1,
        resource_id=10,
        quantity_crafted=5,
        ingredients_used=[{"resource_id": 1, "quantity": 10}],
        profession_id=1,
        profession_level=25,
        experience_gained=50,
        success=True,
        crafting_time_seconds=120
    )
    print(f"✅ Craft log créé: {craft_id}")
    
    # Stats
    stats = service.get_collection_stats()
    print("\n📊 Statistiques collections:")
    for col, data in stats.items():
        print(f"   {col}: {data['count']} docs, {data['size_mb']:.2f} MB")
    
    # Fermeture
    service.close()