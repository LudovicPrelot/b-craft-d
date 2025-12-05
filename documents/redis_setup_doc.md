# ⚡ Redis Setup - B-CraftD v3.0

**Date** : 4 décembre 2025  
**Version** : 3.0.0  
**Statut** : ✅ Configuration complète avec Docker

---

## 🎯 Objectif

Configurer Redis comme **cache temps réel** pour :
- ⚡ **Environnement** (météo, saison) - TTL 1h
- ⚡ **Listings marché actifs** - TTL 1min
- ⚡ **Leaderboard** - TTL 5min
- ⚡ **Inventaires utilisateurs** - TTL 30s
- ⚡ **Sessions utilisateurs** - TTL 24h
- ⚡ **Rate limiting API** - Fenêtres variables

**Gains attendus** :
- -70% requêtes PostgreSQL
- -30% temps réponse API
- +500% capacité utilisateurs simultanés

---

## 📦 Installation avec Docker

### Méthode 1 : Docker Compose (Recommandé)

**Fichier : `docker-compose.yml`** (déjà créé)

```bash
# Démarrer tous les services (PostgreSQL + MongoDB + Redis)
docker-compose up -d

# Démarrer uniquement Redis
docker-compose up -d redis

# Vérifier les logs
docker-compose logs -f redis

# Arrêter
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Méthode 2 : Docker Run (Manuel)

```bash
# Créer volume persistant
docker volume create redis_data

# Lancer Redis avec mot de passe
docker run -d \
  --name bcraftd-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  -v $(pwd)/redis/redis.conf:/usr/local/etc/redis/redis.conf:ro \
  --network bcraftd-network \
  redis:7.2-alpine \
  redis-server /usr/local/etc/redis/redis.conf --requirepass redis_secure_pass

# Vérifier le statut
docker ps | grep redis

# Accéder au CLI
docker exec -it bcraftd-redis redis-cli -a redis_secure_pass
```

### Méthode 3 : Installation Native (Sans Docker)

#### Ubuntu/Debian
```bash
# Ajouter repository Redis
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

# Installer Redis
sudo apt update
sudo apt install redis -y

# Démarrer
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Vérifier
redis-cli ping
# PONG
```

#### macOS
```bash
brew install redis
brew services start redis
```

---

## 🔧 Configuration

### Fichier redis.conf

Placé dans `redis/redis.conf` (configuration optimisée B-CraftD) :

```conf
# Persistence hybride (RDB + AOF)
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# Mémoire
maxmemory 512mb
maxmemory-policy allkeys-lru

# Performance
io-threads 4
io-threads-do-reads yes

# Sécurité
requirepass redis_secure_pass
timeout 300

# Notifications (pour invalidation cache)
notify-keyspace-events "Ex"
```

### Variables d'Environnement (.env)

```bash
REDIS_PASSWORD=redis_secure_pass_change_me
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URI=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}

# TTL Configuration
CACHE_ENVIRONMENT_TTL=3600
CACHE_MARKET_LISTINGS_TTL=60
CACHE_LEADERBOARD_TTL=300
CACHE_USER_INVENTORY_TTL=30
```

### Dépendances Python

```bash
pip install redis==5.0.1
pip install pytest==7.4.3  # Pour tests
```

---

## 🚀 Utilisation du CacheService

### Initialisation

```python
from services.cache_service import CacheService

# Depuis variables d'environnement
import os

cache = CacheService(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    db=int(os.getenv("REDIS_DB", 0)),
    max_connections=50
)
```

### 1. Cache Environnement

```python
# Route: GET /api/environment/current
@router.get("/current")
def get_current_environment(cache: CacheService = Depends(get_cache)):
    # Vérifier cache
    cached = cache.get_current_environment()
    if cached:
        return cached
    
    # Cache MISS: charger depuis DB
    weather = db.query(Weather).filter_by(is_active=True).first()
    season = get_current_season()  # Basé sur le mois actuel
    
    environment = {
        "weather": {
            "id": weather.id,
            "name": weather.name,
            "gathering_multiplier": float(weather.gathering_multiplier),
            "crafting_multiplier": float(weather.crafting_multiplier)
        },
        "season": {
            "id": season.id,
            "name": season.name,
            "gathering_multiplier": float(season.gathering_multiplier),
            "crafting_multiplier": float(season.crafting_multiplier)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Cacher pour 1h
    cache.set_current_environment(environment)
    
    return environment
```

### 2. Cache Marché

```python
# Route: GET /api/market/listings
@router.get("/listings")
def get_market_listings(
    resource_id: Optional[int] = None,
    cache: CacheService = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # Vérifier cache
    cached = cache.get_market_listings(resource_id=resource_id)
    if cached:
        return {"source": "cache", "listings": cached}
    
    # Cache MISS: charger depuis DB
    query = db.query(Market).filter(Market.status_id == 1)  # active
    if resource_id:
        query = query.filter(Market.resource_id == resource_id)
    
    listings = [listing.to_dict() for listing in query.all()]
    
    # Cacher pour 1min
    cache.set_market_listings(listings, resource_id=resource_id)
    
    return {"source": "database", "listings": listings}


# Route: POST /api/market/listings (créer offre)
@router.post("/listings")
def create_listing(
    data: MarketListingCreate,
    cache: CacheService = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # Créer listing en DB
    listing = Market(**data.dict())
    db.add(listing)
    db.commit()
    
    # Invalider cache marché pour cette ressource
    cache.invalidate_market_cache(resource_id=data.resource_id)
    
    return listing


# Route: POST /api/market/listings/{id}/buy (acheter)
@router.post("/listings/{id}/buy")
def buy_listing(
    id: int,
    cache: CacheService = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # ... logique achat ...
    
    # Invalider cache
    cache.invalidate_market_cache(resource_id=listing.resource_id)
    cache.invalidate_user_inventory(buyer_id)
    cache.invalidate_user_inventory(seller_id)
    
    return {"status": "success"}
```

### 3. Cache Leaderboard

```python
# Route: GET /api/leaderboard
@router.get("/leaderboard")
def get_leaderboard(
    limit: int = 100,
    cache: CacheService = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # Vérifier cache
    cached = cache.get_leaderboard(limit=limit)
    if cached:
        return {"source": "cache", "leaderboard": cached}
    
    # Cache MISS: charger depuis DB (ou Vue Matérialisée)
    leaderboard = db.query(mv_leaderboard).limit(limit).all()
    leaderboard_data = [row.to_dict() for row in leaderboard]
    
    # Cacher pour 5min
    cache.set_leaderboard(leaderboard_data, limit=limit)
    
    return {"source": "database", "leaderboard": leaderboard_data}


# Job périodique: Refresh leaderboard (Celery ou APScheduler)
@scheduler.scheduled_job('interval', minutes=5)
def refresh_leaderboard_cache():
    cache = get_cache()
    cache.invalidate_leaderboard()
    logger.info("Leaderboard cache invalidé")
```

### 4. Cache Inventaire

```python
# Route: GET /api/inventory
@router.get("/inventory")
def get_user_inventory(
    user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # Vérifier cache
    cached = cache.get_user_inventory(user.id)
    if cached:
        return {"source": "cache", "inventory": cached}
    
    # Cache MISS
    inventory = db.query(Inventory).filter_by(user_id=user.id).all()
    inventory_data = [item.to_dict() for item in inventory]
    
    # Cacher pour 30s
    cache.set_user_inventory(user.id, inventory_data)
    
    return {"source": "database", "inventory": inventory_data}


# Route: POST /api/craft (invalide inventaire après craft)
@router.post("/craft")
def craft_item(
    data: CraftRequest,
    user: User = Depends(get_current_user),
    cache: CacheService = Depends(get_cache)
):
    # ... logique crafting ...
    
    # Invalider cache inventaire
    cache.invalidate_user_inventory(user.id)
    cache.invalidate_user_recipes(user.id)
    
    return {"status": "success"}
```

### 5. Sessions Utilisateur

```python
# Route: POST /api/auth/login
@router.post("/login")
def login(
    credentials: LoginRequest,
    cache: CacheService = Depends(get_cache),
    db: Session = Depends(get_db)
):
    # Authentifier
    user = authenticate_user(credentials.login, credentials.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Créer session Redis
    session_id = str(uuid.uuid4())
    session_data = {
        "user_id": user.id,
        "login": user.login,
        "role": user.role,
        "created_at": datetime.utcnow().isoformat()
    }
    cache.set_session(session_id, session_data)
    
    # Générer JWT avec session_id
    access_token = create_access_token(data={"sub": user.login, "session_id": session_id})
    
    return {"access_token": access_token, "token_type": "bearer"}


# Route: POST /api/auth/logout
@router.post("/logout")
def logout(
    user: User = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    cache: CacheService = Depends(get_cache)
):
    # Supprimer session Redis
    cache.delete_session(session_id)
    
    return {"status": "logged_out"}


# Middleware: Refresh session sur chaque requête
@app.middleware("http")
async def refresh_session_middleware(request: Request, call_next):
    session_id = request.headers.get("X-Session-ID")
    if session_id:
        cache = get_cache()
        cache.refresh_session(session_id)
    
    response = await call_next(request)
    return response
```

### 6. Rate Limiting

```python
# Middleware: Rate limiting par utilisateur
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    cache = get_cache()
    
    # Identifier l'utilisateur (IP ou user_id)
    identifier = request.client.host
    if hasattr(request.state, "user"):
        identifier = f"user_{request.state.user.id}"
    
    # Vérifier rate limit (60 req/min)
    if not cache.check_rate_limit(identifier, max_requests=60, window_seconds=60):
        remaining = cache.get_remaining_requests(identifier, max_requests=60)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. {remaining} requests remaining."
        )
    
    response = await call_next(request)
    
    # Ajouter headers informatifs
    response.headers["X-RateLimit-Limit"] = "60"
    response.headers["X-RateLimit-Remaining"] = str(cache.get_remaining_requests(identifier, 60))
    
    return response


# Décorateur pour rate limit spécifique
from functools import wraps

def rate_limit(max_requests: int = 10, window: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            user = kwargs.get("user") or kwargs.get("current_user")
            
            identifier = f"endpoint_{func.__name__}_{user.id if user else 'anonymous'}"
            
            if not cache.check_rate_limit(identifier, max_requests, window):
                raise HTTPException(status_code=429, detail="Too many requests")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Utilisation
@router.post("/craft")
@rate_limit(max_requests=10, window=60)  # Max 10 crafts/minute
async def craft_item(data: CraftRequest, user: User = Depends(get_current_user)):
    # ... logique craft ...
    pass
```

---

## 📊 Monitoring & Administration

### Redis CLI (Docker)

```bash
# Accéder au CLI
docker exec -it bcraftd-redis redis-cli -a redis_secure_pass

# Commandes utiles
127.0.0.1:6379> PING
PONG

127.0.0.1:6379> INFO memory
# used_memory_human:45.23M

127.0.0.1:6379> DBSIZE
(integer) 1243

127.0.0.1:6379> KEYS env:*
1) "env:current"
2) "env:weather:current"

127.0.0.1:6379> GET env:current
"{\"weather\":{...}}"

127.0.0.1:6379> TTL env:current
(integer) 3456

127.0.0.1:6379> DEL market:listings:active:10
(integer) 1

127.0.0.1:6379> FLUSHDB
OK
```

### Redis Commander (UI Web)

```bash
# Démarrer avec Docker Compose (profile tools)
docker-compose --profile tools up -d redis-commander

# Accéder: http://localhost:8081
# Credentials: Pas nécessaire (connexion directe)
```

**Fonctionnalités** :
- Visualiser toutes les clés
- Inspecter valeurs JSON
- Supprimer/Modifier clés
- Voir TTL restant
- Statistiques temps réel

### Statistiques Python

```python
from services.cache_service import CacheService

cache = CacheService()

stats = cache.get_stats()
print(f"""
📊 Statistiques Redis
=====================
Clients connectés: {stats['connected_clients']}
Mémoire utilisée: {stats['used_memory_human']}
Mémoire pic: {stats['used_memory_peak_human']}
Commandes traitées: {stats['total_commands_processed']:,}
Hit rate: {stats['hit_rate']:.2f}%
Uptime: {stats['uptime_in_seconds'] / 3600:.1f}h
Version: {stats['redis_version']}
""")
```

---

## 🎯 Stratégies de Cache

### 1. Cache-Aside (Lazy Loading)

**Pattern** : Vérifier cache → MISS → Charger DB → Cacher → Retourner

```python
def get_data(key):
    # 1. Vérifier cache
    data = cache.get(key)
    if data:
        return data  # Cache HIT
    
    # 2. Cache MISS: charger depuis DB
    data = db.query(...).first()
    
    # 3. Cacher
    cache.set(key, data, ttl=300)
    
    # 4. Retourner
    return data
```

**Avantages** :
- Simple à implémenter
- Pas de données inutiles en cache
- Résilient (DB comme source de vérité)

**Inconvénients** :
- Premier accès lent (cold start)
- Cache stampede possible

### 2. Write-Through

**Pattern** : Écrire en DB **ET** en cache simultanément

```python
def update_data(key, data):
    # 1. Écrire en DB
    db.update(...)
    db.commit()
    
    # 2. Écrire en cache
    cache.set(key, data, ttl=300)
    
    return data
```

**Avantages** :
- Cache toujours à jour
- Pas de cache MISS après écriture

**Inconvénients** :
- Latence écriture augmentée
- Données potentiellement inutiles en cache

### 3. Write-Behind (Write-Back)

**Pattern** : Écrire en cache → Async → Écrire en DB

```python
def update_data_async(key, data):
    # 1. Écrire en cache immédiatement
    cache.set(key, data, ttl=300)
    
    # 2. Queue pour écriture DB asynchrone
    celery_task.delay(write_to_db, data)
    
    return data
```

**Avantages** :
- Écriture ultra-rapide
- Réduit charge DB

**Inconvénients** :
- Risque perte données (si Redis crash avant write)
- Complexité accrue

### 4. Invalidation sur Événements

**Pattern** : Invalider cache quand données changent

```python
# Événement: Nouvelle vente sur marché
@market_bp.route("/buy", methods=["POST"])
def buy_item():
    # ... logique achat ...
    
    # Invalider caches impactés
    cache.invalidate_market_cache(resource_id=item.resource_id)
    cache.invalidate_user_inventory(buyer.id)
    cache.invalidate_user_inventory(seller.id)
    cache.invalidate_leaderboard()  # Si impact classement
    
    return {"status": "success"}
```

**Recommandation B-CraftD** :
- **Environnement** : Cache-Aside (change rarement)
- **Marché** : Cache-Aside + Invalidation événements
- **Inventaire** : Invalidation stricte (cohérence critique)
- **Leaderboard** : TTL court (5min) + refresh périodique
- **Sessions** : Write-Through (sécurité)

---

## 🔍 Troubleshooting

### Problème: "Connection refused"

```bash
# Vérifier que Redis tourne
docker ps | grep redis

# Vérifier les logs
docker logs bcraftd-redis

# Redémarrer
docker-compose restart redis
```

### Problème: "NOAUTH Authentication required"

```python
# Vérifier mot de passe dans .env
REDIS_PASSWORD=redis_secure_pass

# Passer le mot de passe au CacheService
cache = CacheService(password=os.getenv("REDIS_PASSWORD"))
```

### Problème: "Out of memory"

```bash
# Vérifier mémoire utilisée
docker exec bcraftd-redis redis-cli -a redis_secure_pass INFO memory

# Augmenter maxmemory dans redis.conf
maxmemory 1gb

# Ou vider le cache
docker exec bcraftd-redis redis-cli -a redis_secure_pass FLUSHDB
```

### Problème: Hit Rate < 50%

**Causes possibles** :
1. TTL trop court → Augmenter TTL
2. Trop d'invalidations → Optimiser stratégie
3. Clés mal conçues → Revoir nomenclature
4. Données rarement consultées → Ne pas cacher

**Solution** :
```python
# Monitorer hit rate
stats = cache.get_stats()
if stats['hit_rate'] < 50:
    logger.warning(f"Hit rate faible: {stats['hit_rate']:.2f}%")
    # Ajuster TTL ou stratégie
```

### Problème: Redis lent

```bash
# Vérifier latence
redis-cli --latency -a redis_secure_pass

# Vérifier slow log
redis-cli -a redis_secure_pass SLOWLOG GET 10

# Optimisations:
# 1. Activer io-threads (redis.conf)
# 2. Utiliser pipeline pour bulk operations
# 3. Éviter KEYS (utiliser SCAN)
```

---

## ✅ Checklist de Déploiement

- [ ] Redis 7.2+ démarré (Docker ou natif)
- [ ] Fichier `redis.conf` configuré (persistence, mémoire, sécurité)
- [ ] Mot de passe Redis défini (`.env`)
- [ ] `redis-py` installé (`pip install redis==5.0.1`)
- [ ] `CacheService` intégré dans l'application
- [ ] Tests `test_cache_service.py` passent (100%)
- [ ] Monitoring configuré (Redis Commander ou CLI)
- [ ] Backup automatique RDB/AOF configuré
- [ ] Rate limiting activé sur API
- [ ] Logs Python configurés (niveau INFO)
- [ ] Hit rate > 70% après 1 semaine

---

## 📚 Ressources

- [Documentation Redis](https://redis.io/docs/)
- [redis-py Documentation](https://redis-py.readthedocs.io/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [Caching Strategies](https://redis.io/docs/manual/patterns/distributed-locks/)

---

**Phase 3 complétée** ✅  
**Prochaine étape** : Phase 4 - Modèles SQLAlchemy

---

**Date de dernière mise à jour** : 4 décembre 2025