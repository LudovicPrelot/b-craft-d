# app/services/cache_service.py
"""
B-CraftD v3.0 - Redis Cache Service
Date: 4 décembre 2025

Service centralisé pour le cache Redis:
- Environnement (météo, saison, biome)
- Listings marché actifs
- Leaderboard
- Inventaires utilisateurs
- Sessions & rate limiting
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import timedelta
from redis import Redis, RedisError, ConnectionPool
from redis.connection import ConnectionPool as RedisConnectionPool
from functools import wraps

logger = logging.getLogger(__name__)


class CacheService:
    """Service centralisé pour tous les caches Redis"""
    
    # Configuration TTL (Time To Live) en secondes
    TTL_ENVIRONMENT = 3600          # 1 heure
    TTL_MARKET_LISTINGS = 60        # 1 minute
    TTL_LEADERBOARD = 300           # 5 minutes
    TTL_USER_INVENTORY = 30         # 30 secondes
    TTL_CURRENT_WEATHER = 3600      # 1 heure
    TTL_RECIPES = 1800              # 30 minutes
    TTL_SESSION = 86400             # 24 heures
    
    # Préfixes de clés
    PREFIX_ENVIRONMENT = "env"
    PREFIX_MARKET = "market"
    PREFIX_LEADERBOARD = "leaderboard"
    PREFIX_INVENTORY = "inv"
    PREFIX_WEATHER = "weather"
    PREFIX_SEASON = "season"
    PREFIX_RECIPES = "recipes"
    PREFIX_SESSION = "session"
    PREFIX_RATE_LIMIT = "ratelimit"
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        max_connections: int = 50,
        decode_responses: bool = True
    ):
        """
        Initialise la connexion Redis avec pool de connexions
        
        Args:
            host: Hôte Redis
            port: Port Redis
            password: Mot de passe Redis (optionnel)
            db: Numéro de base Redis (0-15)
            max_connections: Nombre max de connexions dans le pool
            decode_responses: Décoder automatiquement en UTF-8
        """
        try:
            # Pool de connexions pour performance
            self.pool = ConnectionPool(
                host=host,
                port=port,
                password=password,
                db=db,
                max_connections=max_connections,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            self.redis: Redis = Redis(connection_pool=self.pool)
            
            # Test de connexion
            self.redis.ping()
            logger.info(f"✅ Connexion Redis établie: {host}:{port} (DB {db})")
            
        except RedisError as e:
            logger.error(f"❌ Erreur connexion Redis: {e}")
            raise
    
    # =========================================================================
    # UTILITAIRES GÉNÉRIQUES
    # =========================================================================
    
    def _make_key(self, prefix: str, *parts) -> str:
        """
        Crée une clé Redis formatée
        
        Args:
            prefix: Préfixe de la clé
            *parts: Parties de la clé
            
        Returns:
            str: Clé formatée (ex: "market:listings:active")
        """
        return f"{prefix}:{':'.join(str(p) for p in parts)}"
    
    def _serialize(self, data: Any) -> str:
        """Sérialise les données en JSON"""
        return json.dumps(data, default=str)
    
    def _deserialize(self, data: Union[str, bytes, None]) -> Any:
        """Désérialise les données JSON"""
        if data is None:
            return None
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return json.loads(data)
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Définit une valeur dans Redis
        
        Args:
            key: Clé Redis
            value: Valeur (sera sérialisée en JSON)
            ttl: Time To Live en secondes (None = pas d'expiration)
            nx: Set only if Not eXists
            xx: Set only if eXists
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            serialized = self._serialize(value)
            result = self.redis.set(key, serialized, ex=ttl, nx=nx, xx=xx)
            return bool(result)
        except RedisError as e:
            logger.error(f"Erreur set Redis key={key}: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """
        Récupère une valeur depuis Redis
        
        Args:
            key: Clé Redis
            
        Returns:
            Any: Valeur désérialisée ou None
        """
        try:
            data = self.redis.get(key)
            return self._deserialize(data)
        except RedisError as e:
            logger.error(f"Erreur get Redis key={key}: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """
        Supprime une ou plusieurs clés
        
        Args:
            *keys: Clés à supprimer
            
        Returns:
            int: Nombre de clés supprimées
        """
        try:
            return self.redis.delete(*keys)
        except RedisError as e:
            logger.error(f"Erreur delete Redis keys={keys}: {e}")
            return 0
    
    def exists(self, *keys: str) -> int:
        """
        Vérifie l'existence de clés
        
        Args:
            *keys: Clés à vérifier
            
        Returns:
            int: Nombre de clés existantes
        """
        try:
            return self.redis.exists(*keys)
        except RedisError as e:
            logger.error(f"Erreur exists Redis keys={keys}: {e}")
            return 0
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        Définit une expiration sur une clé
        
        Args:
            key: Clé Redis
            seconds: Secondes avant expiration
            
        Returns:
            bool: Succès
        """
        try:
            return bool(self.redis.expire(key, seconds))
        except RedisError as e:
            logger.error(f"Erreur expire Redis key={key}: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> int:
        """
        Incrémente une valeur
        
        Args:
            key: Clé Redis
            amount: Montant d'incrémentation
            
        Returns:
            int: Nouvelle valeur
        """
        try:
            return self.redis.incrby(key, amount)
        except RedisError as e:
            logger.error(f"Erreur increment Redis key={key}: {e}")
            return 0
    
    def decrement(self, key: str, amount: int = 1) -> int:
        """
        Décrémente une valeur
        
        Args:
            key: Clé Redis
            amount: Montant de décrémentation
            
        Returns:
            int: Nouvelle valeur
        """
        try:
            return self.redis.decrby(key, amount)
        except RedisError as e:
            logger.error(f"Erreur decrement Redis key={key}: {e}")
            return 0
    
    # =========================================================================
    # ENVIRONNEMENT (météo, saison, biome)
    # =========================================================================
    
    def get_current_environment(self) -> Optional[Dict[str, Any]]:
        """
        Récupère l'environnement actuel (météo + saison)
        
        Returns:
            Dict: {weather: {...}, season: {...}, timestamp: ...}
        """
        key = self._make_key(self.PREFIX_ENVIRONMENT, "current")
        return self.get(key)
    
    def set_current_environment(self, environment: Dict[str, Any]) -> bool:
        """
        Cache l'environnement actuel
        
        Args:
            environment: Données environnement
            
        Returns:
            bool: Succès
        """
        key = self._make_key(self.PREFIX_ENVIRONMENT, "current")
        return self.set(key, environment, ttl=self.TTL_ENVIRONMENT)
    
    def get_current_weather(self) -> Optional[Dict[str, Any]]:
        """Récupère la météo actuelle depuis le cache"""
        key = self._make_key(self.PREFIX_WEATHER, "current")
        return self.get(key)
    
    def set_current_weather(self, weather: Dict[str, Any]) -> bool:
        """Cache la météo actuelle"""
        key = self._make_key(self.PREFIX_WEATHER, "current")
        return self.set(key, weather, ttl=self.TTL_CURRENT_WEATHER)
    
    def get_current_season(self) -> Optional[Dict[str, Any]]:
        """Récupère la saison actuelle depuis le cache"""
        key = self._make_key(self.PREFIX_SEASON, "current")
        return self.get(key)
    
    def set_current_season(self, season: Dict[str, Any]) -> bool:
        """Cache la saison actuelle"""
        key = self._make_key(self.PREFIX_SEASON, "current")
        return self.set(key, season, ttl=self.TTL_ENVIRONMENT)
    
    def invalidate_environment(self) -> int:
        """Invalide tous les caches environnement"""
        keys = [
            self._make_key(self.PREFIX_ENVIRONMENT, "current"),
            self._make_key(self.PREFIX_WEATHER, "current"),
            self._make_key(self.PREFIX_SEASON, "current")
        ]
        return self.delete(*keys)
    
    # =========================================================================
    # MARCHÉ
    # =========================================================================
    
    def get_market_listings(
        self,
        resource_id: Optional[int] = None,
        status: str = "active"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère les listings marché depuis le cache
        
        Args:
            resource_id: Filtrer par ressource (None = tous)
            status: Statut des listings
            
        Returns:
            List[Dict]: Liste des listings ou None
        """
        if resource_id:
            key = self._make_key(self.PREFIX_MARKET, "listings", status, resource_id)
        else:
            key = self._make_key(self.PREFIX_MARKET, "listings", status, "all")
        
        return self.get(key)
    
    def set_market_listings(
        self,
        listings: List[Dict[str, Any]],
        resource_id: Optional[int] = None,
        status: str = "active"
    ) -> bool:
        """
        Cache les listings marché
        
        Args:
            listings: Liste des listings
            resource_id: ID ressource (None = tous)
            status: Statut
            
        Returns:
            bool: Succès
        """
        if resource_id:
            key = self._make_key(self.PREFIX_MARKET, "listings", status, resource_id)
        else:
            key = self._make_key(self.PREFIX_MARKET, "listings", status, "all")
        
        return self.set(key, listings, ttl=self.TTL_MARKET_LISTINGS)
    
    def invalidate_market_cache(self, resource_id: Optional[int] = None) -> int:
        """
        Invalide le cache marché
        
        Args:
            resource_id: Ressource spécifique ou None pour tout
            
        Returns:
            int: Nombre de clés supprimées
        """
        if resource_id:
            # Invalider seulement cette ressource
            pattern = f"{self.PREFIX_MARKET}:listings:*:{resource_id}"
        else:
            # Invalider tout le marché
            pattern = f"{self.PREFIX_MARKET}:listings:*"
        
        # Scan pattern (plus sûr que KEYS)
        keys_to_delete = []
        for key in self.redis.scan_iter(match=pattern, count=100):
            keys_to_delete.append(key)
        
        if keys_to_delete:
            return self.delete(*keys_to_delete)
        return 0
    
    # =========================================================================
    # LEADERBOARD
    # =========================================================================
    
    def get_leaderboard(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère le leaderboard depuis le cache
        
        Args:
            limit: Nombre de joueurs (top N)
            
        Returns:
            List[Dict]: Classement ou None
        """
        key = self._make_key(self.PREFIX_LEADERBOARD, "global", limit)
        return self.get(key)
    
    def set_leaderboard(self, leaderboard: List[Dict[str, Any]], limit: int = 100) -> bool:
        """
        Cache le leaderboard
        
        Args:
            leaderboard: Liste des joueurs classés
            limit: Top N
            
        Returns:
            bool: Succès
        """
        key = self._make_key(self.PREFIX_LEADERBOARD, "global", limit)
        return self.set(key, leaderboard, ttl=self.TTL_LEADERBOARD)
    
    def invalidate_leaderboard(self) -> int:
        """Invalide tous les caches leaderboard"""
        pattern = f"{self.PREFIX_LEADERBOARD}:*"
        keys_to_delete = list(self.redis.scan_iter(match=pattern, count=100))
        if keys_to_delete:
            return self.delete(*keys_to_delete)
        return 0
    
    # =========================================================================
    # INVENTAIRE UTILISATEUR
    # =========================================================================
    
    def get_user_inventory(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère l'inventaire d'un utilisateur depuis le cache
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            List[Dict]: Inventaire ou None
        """
        key = self._make_key(self.PREFIX_INVENTORY, user_id)
        return self.get(key)
    
    def set_user_inventory(self, user_id: int, inventory: List[Dict[str, Any]]) -> bool:
        """
        Cache l'inventaire d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            inventory: Liste des items
            
        Returns:
            bool: Succès
        """
        key = self._make_key(self.PREFIX_INVENTORY, user_id)
        return self.set(key, inventory, ttl=self.TTL_USER_INVENTORY)
    
    def invalidate_user_inventory(self, user_id: int) -> int:
        """
        Invalide le cache inventaire d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            int: Nombre de clés supprimées
        """
        key = self._make_key(self.PREFIX_INVENTORY, user_id)
        return self.delete(key)
    
    # =========================================================================
    # RECETTES
    # =========================================================================
    
    def get_craftable_recipes(self, user_id: int, profession_id: int) -> Optional[List[Dict]]:
        """Récupère les recettes craftables pour un utilisateur"""
        key = self._make_key(self.PREFIX_RECIPES, "craftable", user_id, profession_id)
        return self.get(key)
    
    def set_craftable_recipes(
        self,
        user_id: int,
        profession_id: int,
        recipes: List[Dict]
    ) -> bool:
        """Cache les recettes craftables"""
        key = self._make_key(self.PREFIX_RECIPES, "craftable", user_id, profession_id)
        return self.set(key, recipes, ttl=self.TTL_RECIPES)
    
    def invalidate_user_recipes(self, user_id: int) -> int:
        """Invalide toutes les recettes cachées d'un utilisateur"""
        pattern = f"{self.PREFIX_RECIPES}:craftable:{user_id}:*"
        keys_to_delete = list(self.redis.scan_iter(match=pattern, count=100))
        if keys_to_delete:
            return self.delete(*keys_to_delete)
        return 0
    
    # =========================================================================
    # SESSIONS UTILISATEUR
    # =========================================================================
    
    def set_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Crée une session utilisateur
        
        Args:
            session_id: ID de session (UUID)
            user_data: Données utilisateur
            
        Returns:
            bool: Succès
        """
        key = self._make_key(self.PREFIX_SESSION, session_id)
        return self.set(key, user_data, ttl=self.TTL_SESSION)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une session"""
        key = self._make_key(self.PREFIX_SESSION, session_id)
        return self.get(key)
    
    def delete_session(self, session_id: str) -> int:
        """Supprime une session (logout)"""
        key = self._make_key(self.PREFIX_SESSION, session_id)
        return self.delete(key)
    
    def refresh_session(self, session_id: str) -> bool:
        """Prolonge la durée d'une session"""
        key = self._make_key(self.PREFIX_SESSION, session_id)
        return self.expire(key, self.TTL_SESSION)
    
    # =========================================================================
    # RATE LIMITING
    # =========================================================================
    
    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> bool:
        """
        Vérifie si une requête respecte la limite de taux
        
        Args:
            identifier: Identifiant (user_id, IP, etc.)
            max_requests: Nombre max de requêtes
            window_seconds: Fenêtre de temps (secondes)
            
        Returns:
            bool: True si autorisé, False si limite dépassée
        """
        try:
            key = self._make_key(self.PREFIX_RATE_LIMIT, identifier)
            
            # Incrémenter le compteur
            current = self.redis.incr(key)
            
            # Définir expiration lors de la première requête
            if current == 1:
                self.redis.expire(key, window_seconds)
            
            # Vérifier la limite
            return current <= max_requests
            
        except RedisError as e:
            logger.error(f"Erreur rate limit: {e}")
            return True  # En cas d'erreur Redis, autoriser la requête
    
    def get_remaining_requests(
        self,
        identifier: str,
        max_requests: int = 60
    ) -> int:
        """
        Récupère le nombre de requêtes restantes
        
        Args:
            identifier: Identifiant
            max_requests: Limite max
            
        Returns:
            int: Requêtes restantes
        """
        try:
            key = self._make_key(self.PREFIX_RATE_LIMIT, identifier)
            current = int(self.redis.get(key) or 0)
            return max(0, max_requests - current)
        except RedisError:
            return max_requests
    
    # =========================================================================
    # STATISTIQUES & MONITORING
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques Redis
        
        Returns:
            Dict: Statistiques serveur
        """
        try:
            info = self.redis.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "redis_version": info.get("redis_version", "unknown")
            }
        except RedisError as e:
            logger.error(f"Erreur get_stats: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calcule le taux de hit du cache"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    def flush_all(self) -> bool:
        """
        ⚠️ DANGER: Supprime TOUTES les clés Redis
        
        Returns:
            bool: Succès
        """
        try:
            self.redis.flushdb()
            logger.warning("🗑️ Cache Redis vidé complètement")
            return True
        except RedisError as e:
            logger.error(f"Erreur flush_all: {e}")
            return False
    
    def close(self):
        """Ferme la connexion Redis"""
        try:
            self.redis.close()
            logger.info("Connexion Redis fermée")
        except RedisError as e:
            logger.error(f"Erreur fermeture Redis: {e}")


# =========================================================================
# DÉCORATEUR DE CACHE
# =========================================================================

def cached(ttl: int = 300, key_prefix: str = "cached"):
    """
    Décorateur pour cacher automatiquement le résultat d'une fonction
    
    Args:
        ttl: Time To Live en secondes
        key_prefix: Préfixe de la clé Redis
        
    Example:
        @cached(ttl=600, key_prefix="user")
        def get_user_data(user_id: int):
            return db.query(User).filter_by(id=user_id).first()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Créer une clé unique basée sur les arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # TODO: Injecter CacheService via dependency injection
            # Pour l'instant, instancier localement (à améliorer)
            try:
                cache = CacheService()
                
                # Vérifier le cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached_result
                
                # Cache MISS: exécuter la fonction
                logger.debug(f"Cache MISS: {cache_key}")
                result = func(*args, **kwargs)
                
                # Cacher le résultat
                cache.set(cache_key, result, ttl=ttl)
                
                return result
                
            except Exception as e:
                logger.error(f"Erreur cache decorator: {e}")
                # En cas d'erreur, exécuter la fonction normalement
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# =========================================================================
# EXEMPLE D'UTILISATION
# =========================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialisation
    cache = CacheService(
        host="localhost",
        port=6379,
        password="redis_secure_pass",
        db=0
    )
    
    # Test environnement
    cache.set_current_weather({
        "id": 1,
        "name": "Ensoleillé",
        "gathering_multiplier": 1.0,
        "crafting_multiplier": 1.0
    })
    print(f"✅ Météo cachée: {cache.get_current_weather()}")
    
    # Test market
    cache.set_market_listings([
        {"id": 1, "resource_id": 10, "price": 100.0},
        {"id": 2, "resource_id": 10, "price": 95.0}
    ], resource_id=10)
    print(f"✅ Listings cachés: {cache.get_market_listings(resource_id=10)}")
    
    # Test rate limiting
    for i in range(5):
        allowed = cache.check_rate_limit("user_123", max_requests=3, window_seconds=60)
        print(f"Requête {i+1}: {'✅ Autorisée' if allowed else '❌ Bloquée'}")
    
    # Stats
    stats = cache.get_stats()
    print(f"\n📊 Stats Redis: Hit rate = {stats.get('hit_rate', 0):.2f}%")
    
    # Fermeture
    cache.close()