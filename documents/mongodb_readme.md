# 📊 MongoDB Setup - B-CraftD v3.0

**Date** : 4 décembre 2025  
**Version** : 3.0.0  
**Statut** : ✅ Configuration complète

---

## 🎯 Objectif

Configurer MongoDB comme base de données **secondaire** pour stocker :
- 📝 **Logs d'audit** (CRUD operations) - TTL 180 jours
- ⚒️ **Historique de crafting** complet - Permanent
- 💰 **Transactions marché** complètes - Permanent
- 📈 **Métriques utilisateurs** (time-series) - TTL 90 jours
- 💬 **Messages de chat** - TTL 90 jours

---

## 📦 Prérequis

### Installation MongoDB

#### Ubuntu/Debian
```bash
# Import clé GPG
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Ajouter repository
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] \
   https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Installer
sudo apt update
sudo apt install -y mongodb-org

# Démarrer
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS (Homebrew)
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

#### Windows
Télécharger depuis : https://www.mongodb.com/try/download/community

### Dépendances Python
```bash
pip install pymongo==4.6.0
pip install pytest==7.4.3  # Pour tests
```

---

## 🚀 Installation

### Étape 1 : Créer les Collections MongoDB

```bash
# Exécuter le script de setup 
# Remplacer variables par valeur
mongosh --port 27017  --authenticationDatabase "admin" -u "$MONGO_INITDB_ROOT_USERNAME$" -p "$MONGO_INITDB_ROOT_PASSWORD" < mongodb_setup_v3.js

# Ou avec mongo (versions anciennes)
mongo < mongodb_setup_v3.js
```

**Sortie attendue** :
```
🚀 B-CraftD v3.0 - Configuration MongoDB
=========================================

✅ audit_logs créée avec 5 index + TTL 180 jours
✅ crafting_history créée avec 6 index (pas de TTL)
✅ market_transactions créée avec 5 index (pas de TTL)
✅ user_metrics créée (time-series) avec TTL 90 jours
✅ chat_messages créée avec 5 index + TTL 90 jours

✅ 5 documents de test insérés
✅ Configuration MongoDB terminée avec succès !
```

### Étape 2 : Configurer l'Application Python

**Fichier : `config/settings.py`**
```python
# Configuration MongoDB
MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DB_NAME = "bcraftd"

# Pour production avec authentification
# MONGODB_URI = "mongodb://username:password@localhost:27017/"
```

### Étape 3 : Tester la Connexion

```bash
python -m pytest tests/test_mongodb_logging.py -v
```

**Résultat attendu** : Tous les tests passent ✅

---

## 📊 Architecture des Collections

### 1. audit_logs (TTL: 180 jours)

**Usage** : Traçabilité complète des actions utilisateurs

**Structure** :
```javascript
{
  _id: ObjectId("..."),
  user_id: 1,                    // INT (référence PostgreSQL)
  action: "INSERT",              // ENUM: INSERT|UPDATE|DELETE|SELECT
  table_name: "users",
  record_id: 123,
  old_values: {...},             // Pour UPDATE/DELETE
  new_values: {...},             // Pour INSERT/UPDATE
  ip_address: "192.168.1.1",
  user_agent: "Mozilla/5.0...",
  timestamp: ISODate("2025-12-04T10:30:00Z")
}
```

**Index** :
- `{user_id: 1, timestamp: -1}` - Historique par utilisateur
- `{table_name: 1, timestamp: -1}` - Logs par table
- `{action: 1, timestamp: -1}` - Filtrage par action
- `{record_id: 1, table_name: 1}` - Recherche enregistrement
- `{timestamp: 1}` expireAfterSeconds: 15552000 (180j) - TTL

### 2. crafting_history (Permanent)

**Usage** : Analytics crafting, taux de réussite, optimisation

**Structure** :
```javascript
{
  _id: ObjectId("..."),
  user_id: 1,
  recipe_id: 5,
  resource_id: 25,
  quantity_crafted: 10,
  ingredients_used: [
    {resource_id: 1, quantity: 20},
    {resource_id: 2, quantity: 10}
  ],
  workshop_id: 3,                        // Optionnel
  workshop_durability_before: 100,
  workshop_durability_after: 95,
  profession_id: 1,
  profession_level: 30,
  experience_gained: 75,
  success: true,
  crafting_time_seconds: 300,
  weather_bonus: 1.2,
  season_bonus: 1.0,
  mastery_bonus: 1.25,
  crafted_at: ISODate("2025-12-04T10:35:00Z")
}
```

**Index** :
- `{user_id: 1, crafted_at: -1}` - Historique utilisateur
- `{recipe_id: 1, crafted_at: -1}` - Analytics par recette
- `{resource_id: 1, crafted_at: -1}` - Production ressource
- `{profession_id: 1, crafted_at: -1}` - Stats profession
- `{success: 1, crafted_at: -1}` - Taux de réussite
- `{crafted_at: -1}` - Timeline globale

### 3. market_transactions (Permanent)

**Usage** : Analytics économie, historique prix, tendances

**Structure** :
```javascript
{
  _id: ObjectId("..."),
  market_id: 1234,                      // Référence markets(id)
  seller_id: 1,
  buyer_id: 2,
  resource_id: 50,
  quantity: 10,
  unit_price: 150.50,
  total_price: 1505.00,
  seller_coins_before: 1000.00,
  seller_coins_after: 2505.00,
  buyer_coins_before: 5000.00,
  buyer_coins_after: 3495.00,
  listing_duration_hours: 2.5,
  market_fee: 15.05,
  transaction_date: ISODate("2025-12-04T10:40:00Z"),
  created_at: ISODate("2025-12-04T08:10:00Z")
}
```

**Index** :
- `{seller_id: 1, transaction_date: -1}` - Ventes utilisateur
- `{buyer_id: 1, transaction_date: -1}` - Achats utilisateur
- `{resource_id: 1, transaction_date: -1}` - Évolution prix
- `{transaction_date: -1}` - Tendances temporelles
- `{unit_price: 1, resource_id: 1}` - Analyse prix

### 4. user_metrics (Time-Series, TTL: 90 jours)

**Usage** : Progression joueurs, graphiques temps réel, dashboards

**Structure** :
```javascript
{
  _id: ObjectId("..."),
  user_id: 1,                           // metaField
  timestamp: ISODate("2025-12-04T10:00:00Z"),  // timeField
  level: 30,
  experience: 7500,
  coins: 2500.50,
  active_professions: 2,
  total_profession_levels: 65,
  inventory_slots_used: 45,
  inventory_total_value: 15000.00,
  active_market_listings: 5,
  crafts_last_hour: 12,
  resources_gathered_last_hour: 35,
  sales_last_hour: 2,
  purchases_last_hour: 1,
  online_status: true
}
```

**Index** :
- `{user_id: 1, timestamp: -1}` - Timeline utilisateur
- `{timestamp: 1}` expireAfterSeconds: 7776000 (90j) - TTL

**Granularité** : 1 document/heure/utilisateur

### 5. chat_messages (TTL: 90 jours)

**Usage** : Historique chat, modération, support

**Structure** :
```javascript
{
  _id: ObjectId("..."),
  user_id: 1,
  username: "player123",               // Dénormalisé pour perf
  message: "Bonjour tout le monde !",
  channel: "global",                   // global|trade|profession|guild|whisper
  recipient_id: null,                  // Pour whisper
  guild_id: null,                      // Pour chat guilde
  is_system_message: false,
  sent_at: ISODate("2025-12-04T10:45:00Z")
}
```

**Index** :
- `{channel: 1, sent_at: -1}` - Messages par canal
- `{user_id: 1, sent_at: -1}` - Messages utilisateur
- `{recipient_id: 1, sent_at: -1}` - Whispers reçus
- `{guild_id: 1, sent_at: -1}` - Chat guilde
- `{sent_at: 1}` expireAfterSeconds: 7776000 (90j) - TTL

---

## 🔧 Utilisation du LoggingService

### Initialisation

```python
from services.logging_service import LoggingService

# Initialiser le service
logging_service = LoggingService(
    mongo_uri="mongodb://localhost:27017/",
    db_name="bcraftd"
)
```

### Exemples d'Utilisation

#### 1. Logger une Action d'Audit

```python
# Après un INSERT en PostgreSQL
logging_service.log_audit(
    user_id=current_user.id,
    action="INSERT",
    table_name="inventory",
    record_id=new_item.id,
    new_values={"resource_id": 10, "quantity": 5},
    ip_address=request.remote_addr,
    user_agent=request.headers.get("User-Agent")
)
```

#### 2. Logger un Craft

```python
# Après crafting réussi
logging_service.log_craft(
    user_id=user.id,
    recipe_id=recipe.id,
    resource_id=recipe.resource_id,
    quantity_crafted=recipe.output_quantity,
    ingredients_used=[
        {"resource_id": ing.resource_id, "quantity": ing.quantity}
        for ing in recipe.ingredients
    ],
    profession_id=user_profession.profession_id,
    profession_level=user_profession.level,
    experience_gained=recipe.base_experience,
    success=True,
    crafting_time_seconds=recipe.crafting_time,
    weather_bonus=current_weather_multiplier,
    season_bonus=current_season_multiplier,
    mastery_bonus=user_profession.mastery_rank.bonus_multiplier,
    workshop_id=workshop.id if workshop else None,
    workshop_durability_before=workshop.durability if workshop else None,
    workshop_durability_after=workshop.durability - 5 if workshop else None
)
```

#### 3. Logger une Transaction Marché

```python
# Après vente complétée
logging_service.log_market_transaction(
    market_id=market_listing.id,
    seller_id=market_listing.seller_id,
    buyer_id=buyer.id,
    resource_id=market_listing.resource_id,
    quantity=market_listing.quantity,
    unit_price=market_listing.unit_price,
    total_price=market_listing.total_price,
    seller_coins_before=seller_coins_before,
    seller_coins_after=seller.coins,
    buyer_coins_before=buyer_coins_before,
    buyer_coins_after=buyer.coins,
    listing_duration_hours=(datetime.utcnow() - market_listing.created_at).total_seconds() / 3600,
    created_at=market_listing.created_at,
    market_fee=market_listing.total_price * 0.01  # 1% frais
)
```

#### 4. Logger Métriques Utilisateur (Toutes les heures)

```python
# Job planifié (cron ou Celery beat)
@celery.task
def log_user_metrics_hourly():
    active_users = User.query.filter_by(is_active=True).all()
    
    for user in active_users:
        inventory_value = db.session.query(
            func.sum(Inventory.quantity * Resource.base_value * Rarity.multiplier)
        ).join(Resource).join(Rarity).filter(Inventory.user_id == user.id).scalar() or 0
        
        logging_service.log_user_metrics(
            user_id=user.id,
            level=user.level,
            experience=user.experience,
            coins=user.coins,
            active_professions=len(user.professions),
            total_profession_levels=sum(p.level for p in user.professions),
            inventory_slots_used=len(user.inventory),
            inventory_total_value=inventory_value,
            active_market_listings=Market.query.filter_by(seller_id=user.id, status_id=1).count(),
            online_status=user.last_login > datetime.utcnow() - timedelta(minutes=5)
        )
```

#### 5. Logger Message de Chat

```python
# Route /api/chat/send
@chat_bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    data = request.json
    user = get_current_user()
    
    # Sauvegarder en temps réel (optionnel en DB)
    # emit via WebSocket...
    
    # Logger dans MongoDB
    logging_service.log_chat_message(
        user_id=user.id,
        username=user.login,
        message=data["message"],
        channel=data["channel"],
        recipient_id=data.get("recipient_id"),
        guild_id=user.guild_id if data["channel"] == "guild" else None
    )
    
    return jsonify({"status": "sent"})
```

### Récupération de Données

```python
# Historique audit d'un utilisateur
audit_history = logging_service.get_user_audit_history(user_id=1, limit=50)

# Historique craft
craft_history = logging_service.get_user_craft_history(user_id=1, success_only=True)

# Taux de réussite d'une recette
recipe_stats = logging_service.get_recipe_success_rate(recipe_id=5, days=30)
# {'total_attempts': 120, 'successes': 95, 'failures': 25, 'success_rate': 79.17}

# Analytics marché
market_analytics = logging_service.get_market_analytics(resource_id=10, days=7)
# {'total_transactions': 45, 'total_volume': 230, 'avg_unit_price': 125.50, ...}

# Timeline progression utilisateur
timeline = logging_service.get_user_progression_timeline(user_id=1, hours=24)

# Historique chat
chat_history = logging_service.get_chat_history(channel="global", limit=100)

# Statistiques collections
stats = logging_service.get_collection_stats()
```

---

## 📈 Estimations de Volumétrie

### Scénario : 10,000 utilisateurs actifs

| Collection | Docs/Jour | Docs/Mois | Taille (1 mois) | TTL |
|------------|-----------|-----------|-----------------|-----|
| audit_logs | 500k | 15M | ~5 GB | 180j |
| crafting_history | 100k | 3M | ~1 GB | Permanent |
| market_transactions | 50k | 1.5M | ~500 MB | Permanent |
| user_metrics | 240k | 7.2M | ~2 GB | 90j |
| chat_messages | 200k | 6M | ~1 GB | 90j |

**Total espace disque (avec TTL actifs)** : ~15 GB/mois stabilisé

### Scénario : 100,000 utilisateurs actifs

| Collection | Docs/Mois | Taille (1 mois) | Stockage Annuel |
|------------|-----------|-----------------|------------------|
| audit_logs | 150M | 50 GB | 50 GB (rotation) |
| crafting_history | 30M | 10 GB | 120 GB |
| market_transactions | 15M | 5 GB | 60 GB |
| user_metrics | 72M | 20 GB | 20 GB (rotation) |
| chat_messages | 60M | 10 GB | 10 GB (rotation) |

**Total** : ~250 GB/an

---

## 🔍 Requêtes Utiles MongoDB

### Monitoring

```javascript
// Vérifier statut serveur
db.serverStatus()

// Stats collection
db.audit_logs.stats()

// Vérifier TTL index
db.audit_logs.getIndexes()

// Nombre de documents
db.audit_logs.countDocuments()

// Taille collection
db.audit_logs.stats().size / (1024 * 1024)  // MB
```

### Maintenance

```javascript
// Purge manuelle (avant TTL)
db.audit_logs.deleteMany({
  timestamp: { $lt: new Date('2024-06-01') }
})

// Reconstruire index
db.audit_logs.reIndex()

// Compact collection (libérer espace)
db.runCommand({ compact: 'audit_logs' })

// Vérifier documents expirés
db.audit_logs.find({
  timestamp: { $lt: new Date(Date.now() - 180*24*60*60*1000) }
}).count()
```

### Analytics Avancées

```javascript
// Top 10 joueurs les plus actifs (crafting)
db.crafting_history.aggregate([
  { $group: {
    _id: "$user_id",
    total_crafts: { $sum: 1 },
    total_xp: { $sum: "$experience_gained" }
  }},
  { $sort: { total_crafts: -1 } },
  { $limit: 10 }
])

// Ressources les plus vendues
db.market_transactions.aggregate([
  { $group: {
    _id: "$resource_id",
    total_transactions: { $sum: 1 },
    total_volume: { $sum: "$quantity" },
    avg_price: { $avg: "$unit_price" }
  }},
  { $sort: { total_volume: -1 } },
  { $limit: 10 }
])

// Évolution prix d'une ressource (7 derniers jours)
db.market_transactions.aggregate([
  { $match: {
    resource_id: 50,
    transaction_date: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
  }},
  { $group: {
    _id: { $dateToString: { format: "%Y-%m-%d", date: "$transaction_date" } },
    avg_price: { $avg: "$unit_price" },
    min_price: { $min: "$unit_price" },
    max_price: { $max: "$unit_price" },
    volume: { $sum: "$quantity" }
  }},
  { $sort: { _id: 1 } }
])
```

---

## 🔄 Archivage Automatique PostgreSQL → MongoDB

**Service Ã  implémenter (Phase 5)** : `services/archival_service.py`

```python
class ArchivalService:
    """Archive les anciennes données PostgreSQL vers MongoDB"""
    
    @staticmethod
    def archive_old_markets():
        """
        Archive markets > 6 mois vers MongoDB
        Purge de PostgreSQL après confirmation
        """
        threshold = datetime.utcnow() - timedelta(days=180)
        
        # Sélectionner anciennes transactions
        old_markets = Market.query.filter(
            Market.completed_at < threshold,
            Market.status_id == 2  # sold
        ).all()
        
        # Insérer dans MongoDB
        for market in old_markets:
            logging_service.log_market_transaction(
                market_id=market.id,
                seller_id=market.seller_id,
                buyer_id=market.buyer_id,
                # ... autres champs
            )
        
        # Supprimer de PostgreSQL
        Market.query.filter(
            Market.completed_at < threshold,
            Market.status_id == 2
        ).delete()
        
        db.session.commit()
        logger.info(f"Archivé {len(old_markets)} transactions marché")
```

**Configuration cron** :
```bash
# Tous les jours à 2h du matin
0 2 * * * python -m scripts.archive_old_data
```

---

## ✅ Checklist de Déploiement

- [ ] MongoDB 7.0+ installé et démarré
- [ ] Script `mongodb_setup_v3.js` exécuté avec succès
- [ ] 5 collections créées avec index
- [ ] TTL index actifs (audit_logs, user_metrics, chat_messages)
- [ ] `pymongo` installé dans venv Python
- [ ] `LoggingService` intégré dans l'application
- [ ] Tests `test_mongodb_logging.py` passent (100%)
- [ ] Monitoring configuré (MongoDB Compass ou mongotop)
- [ ] Backup automatique configuré (mongodump cron)
- [ ] Logs Python configurés (niveau INFO minimum)

---

## 🛠️ Troubleshooting

### Erreur: "Connection refused"
```bash
# Vérifier statut MongoDB
sudo systemctl status mongod

# Redémarrer
sudo systemctl restart mongod

# Vérifier logs
sudo tail -f /var/log/mongodb/mongod.log
```

### Erreur: "Authentication failed"
```python
# Créer utilisateur MongoDB
use admin
db.createUser({
  user: "bcraftd_user",
  pwd: "secure_password",
  roles: [ { role: "readWrite", db: "bcraftd" } ]
})

# Modifier MONGODB_URI
MONGODB_URI = "mongodb://bcraftd_user:secure_password@localhost:27017/bcraftd"
```

### TTL Index ne fonctionne pas
```javascript
// Vérifier thread TTL actif
db.serverStatus().metrics.ttl

// Forcer exécution TTL (debug uniquement)
db.runCommand({ compact: 'audit_logs', force: true })
```

---

## 📚 Ressources

- [Documentation MongoDB](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Time-Series Collections](https://www.mongodb.com/docs/manual/core/timeseries-collections/)
- [TTL Indexes](https://www.mongodb.com/docs/manual/core/index-ttl/)

---

**Phase 2 complétée** ✅  
**Prochaine étape** : Phase 3 - Redis Setup

---

**Date de dernière mise à jour** : 4 décembre 2025