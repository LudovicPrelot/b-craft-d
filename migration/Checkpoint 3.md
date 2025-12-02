# 📚 CHECKPOINT V3 - Migration PostgreSQL B-CraftD

**Date de création:** 2025-01-15  
**Version:** 3.0  
**Progression globale:** ~60%  
**Statut:** Authentification PostgreSQL complète ✅

---

## 🎯 État actuel du projet

### ✅ TERMINÉ (Critical Path)

#### 1. Infrastructure PostgreSQL (100%)
- ✅ Docker Compose avec service postgres:16-alpine
- ✅ Connexion testée et fonctionnelle
- ✅ Variables d'environnement configurées (.env)
- ✅ Health check PostgreSQL configuré
- ✅ **Patch SQLAlchemy mémorisé:** Toujours utiliser `text()` pour SQL brut

#### 2. Architecture modulaire des modèles (100%)
**IMPORTANT:** Les modèles sont dans `database/models/` (PAS `app/models/`)

```
database/
├── connection.py ✅
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── profession.py
│   ├── resource.py
│   ├── recipe.py
│   └── refresh_token.py
```

**Avantages:**
- Chargement sélectif des modèles (performances)
- Fichiers focalisés et maintenables
- Séparation claire des responsabilités

#### 3. Migration des données (100%)
- ✅ Script `scripts/migrate_json_to_postgres.py` exécuté
- ✅ Toutes les données transférées avec succès
- ✅ Fichiers JSON conservés en backup (`storage/`)
- ✅ Tables créées et indexées

#### 4. Schémas Pydantic (50% - 4/8 entités)
- ✅ `schemas/profession.py` (Create, Update, Response)
- ✅ `schemas/resource.py` (Create, Update, Response)
- ✅ `schemas/recipe.py` (Create, Update, Response, avec validators)
- ✅ `schemas/user.py` (Create, Update, Response, ProfileResponse)
- ⏸️ `schemas/inventory.py` (à créer)
- ⏸️ `schemas/crafting.py` (à créer)
- ⏸️ `schemas/loot.py` (à créer)
- ⏸️ `schemas/quest.py` (à créer)

#### 5. Authentification PostgreSQL (100%) 🎉
**NOUVEAU - CRITIQUE DÉBLOQUÉ**

**Fichiers refactorisés:**
- ✅ `utils/auth.py` - Toutes les fonctions utilisent PostgreSQL
  - `store_refresh_token(db, ...)` - Stockage dans table refresh_tokens
  - `revoke_refresh_token(db, ...)` - Révocation atomique
  - `rotate_refresh_token(db, ...)` - Rotation sécurisée
  - `get_active_devices(db, ...)` - Requête avec filtre expiration
  - `cleanup_expired_tokens(db)` - Nettoyage automatique
  - Hash PBKDF2 inchangé (déjà sécurisé)

- ✅ `routes/api/public/auth.py` - Toutes les routes utilisent DB
  - `POST /login` - Stocke refresh token dans PostgreSQL
  - `POST /refresh` - Rotation avec vérification DB
  - `POST /logout` - Révoque depuis PostgreSQL
  - `POST /logout_all` - Révoque tous les tokens user
  - `GET /devices` - Liste devices actifs (déplacé depuis /user/me)
  - `POST /devices/{device_id}/revoke` - Révoque device spécifique

**Script de maintenance:**
- ✅ `scripts/cleanup_expired_tokens.py` - Nettoyage cron

**Impact:** Plus aucun fichier JSON utilisé pour l'authentification

#### 6. Routes API migrées (46% - 11/24)

**Admin (57% - 4/7)**
- ✅ `routes/api/admin/professions.py` - CRUD complet + validation
- ✅ `routes/api/admin/resources.py` - CRUD + recherche + stats
- ✅ `routes/api/admin/recipes.py` - CRUD + validation intégrité
- ⏸️ `routes/api/admin/users.py` - À migrer
- ⏸️ `routes/api/admin/loot.py` - À migrer
- ⏸️ `routes/api/admin/settings.py` - À migrer
- ⚠️ `routes/api/admin/dispatcher.py` - **À SUPPRIMER** (remplacé par TestClient)

**Public (100% - 4/4)** 🎉
- ✅ `routes/api/public/professions.py` - Lecture seule
- ✅ `routes/api/public/resources.py` - Lecture seule
- ✅ `routes/api/public/recipes.py` - Lecture seule
- ✅ `routes/api/public/auth.py` - Authentification complète
- ⏸️ `routes/api/public/quests.py` - À migrer (feature flag)

**User (40% - 4/10)**
- ✅ `routes/api/user/professions.py` - Lecture
- ✅ `routes/api/user/resources.py` - Lecture
- ✅ `routes/api/user/recipes.py` - Lecture
- ✅ `routes/api/user/me.py` - Profil (devices déplacés vers /auth/devices)
- ⏸️ `routes/api/user/inventory.py` - À migrer (PRIORITÉ)
- ⏸️ `routes/api/user/crafting.py` - À migrer (PRIORITÉ)
- ⏸️ `routes/api/user/stats.py` - À migrer
- ⏸️ `routes/api/user/loot.py` - À migrer
- ⏸️ `routes/api/user/quests.py` - À migrer
- ⏸️ `routes/api/user/dashboard.py` - À migrer

---

## 🚧 EN COURS / PRIORITÉS

### Priorité 1: CRITIQUE - Routes User métier (2 jours)
**Bloquant:** Fonctionnalités core du jeu

**Fichiers à migrer:**
1. `routes/api/user/inventory.py` - Add/remove items
2. `routes/api/user/crafting.py` - Craft avec validation
3. `routes/api/user/stats.py` - XP, level up

**Prérequis:** Migrer les services métier d'abord

### Priorité 2: HAUTE - Services métier (1 jour)
**Impact:** Logique business réutilisable

**Fichiers à adapter:**
1. `services/inventory_service.py` - Utiliser SQLAlchemy
2. `services/crafting_service.py` - Utiliser SQLAlchemy
3. `services/xp_service.py` - ✅ OK (pas de stockage)

**Pattern de migration:**
```python
# ❌ AVANT (JSON)
def add_item(user: User, item: str, qty: int):
    user.inventory[item] = user.inventory.get(item, 0) + qty
    users = load_json(USERS_FILE)
    users[user.id] = user.to_dict()
    save_json(USERS_FILE, users)

# ✅ APRÈS (PostgreSQL)
def add_item(db: Session, user: User, item: str, qty: int):
    user.inventory[item] = user.inventory.get(item, 0) + qty
    db.commit()
    db.refresh(user)
```

### Priorité 3: MOYENNE - Routes Admin restantes (1 jour)
1. `routes/api/admin/users.py` - CRUD + grant_xp
2. `routes/api/admin/loot.py` - Tables de loot
3. `routes/api/admin/settings.py` - Feature flags

### Priorité 4: CLEANUP - Suppression code legacy (2h)
**Fichiers à supprimer:**
- ⚠️ `utils/crud.py` - Remplacé par `db_crud.py`
- ⚠️ `utils/json.py` - Plus nécessaire (PostgreSQL)
- ⚠️ `utils/local_api_dispatcher.py` - **Over-engineering**
- ⚠️ `utils/client.py` - Remplacer par `TestClient`
- ⚠️ `database/database.py` - Ancien système de validation
- ⚠️ `generated/` - Jamais utilisé
- ⚠️ `scripts/fix_bugs.py` - Script one-off

**Action:** Créer `utils/test_client.py` avec TestClient FastAPI

---

## 🔧 Correctifs techniques identifiés

### 1. Fix `init_db()` pour imports modulaires

**Problème:** Import `from database import models` échoue

**Solution:**
```python
def init_db():
    """Crée toutes les tables définies dans Base.metadata."""
    logger.info("🔧 Initialisation de la base de données...")
    
    # Import tous les modèles individuellement
    from database.models import User, Profession, Resource, Recipe, RefreshToken
    
    # Crée les tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Tables créées avec succès")
```

### 2. Remplacement du dispatcher par TestClient

**Fichier à créer:** `utils/test_client.py`

**Utilisation:**
```python
# Au lieu de:
from utils.client import api_get
result = await api_get("/api/public/professions")

# Utiliser:
from utils.test_client import test_client
response = test_client.get("/api/public/professions")
result = response.json()
```

---

## 📊 Métriques de progression détaillées

### Avancement global: ~60%
- ✅ Infrastructure: 100%
- ✅ Modèles modulaires: 100%
- ✅ Migration données: 100%
- ✅ Authentification: 100% 🎉
- ⏸️ Schémas Pydantic: 50% (4/8)
- ⏸️ Routes API: 46% (11/24)
  - Admin: 57% (4/7)
  - Public: 100% (4/4) 🎉
  - User: 40% (4/10)
- ⏸️ Services: 33% (1/3 - xp_service OK)
- ⏸️ Tests: 0%
- ⏸️ Cleanup: 0%

### Temps estimé restant: 3-4 jours
- Services métier: 1 jour
- Routes User métier: 1 jour
- Routes Admin restantes: 1 jour
- Tests: 1 jour
- Cleanup: quelques heures

---

## 🎓 Bonnes pratiques établies

### 1. Architecture modulaire des modèles ✅
**Structure:**
```
database/models/
├── __init__.py      # Import centralisé
├── user.py          # ~50 lignes
├── profession.py    # ~30 lignes
├── resource.py      # ~30 lignes
├── recipe.py        # ~30 lignes
└── refresh_token.py # ~20 lignes
```

**Import sélectif:**
```python
# Charge uniquement ce dont on a besoin
from database.models import User, Profession
```

### 2. Validation Pydantic systématique ✅
**3 schémas par entité:**
- `EntityCreate` - Tous champs requis
- `EntityUpdate` - Tous optionnels avec `exclude_unset=True`
- `EntityResponse` - Avec `from_attributes = True`

### 3. Transactions SQLAlchemy ✅
```python
@router.post("/craft")
def craft(recipe_id: str, user=Depends(...), db: Session = Depends(get_db)):
    try:
        # Modifications atomiques
        user.inventory[item] -= qty
        db.commit()
        db.refresh(user)
        return user.to_dict()
    except Exception:
        db.rollback()
        raise
```

### 4. SQL brut avec text() ✅
**TOUJOURS wrapper avec `text()`:**
```python
from sqlalchemy import text

# ✅ CORRECT
db.execute(text("SELECT NOW()"))
db.query(User).filter(text("level > 50")).all()

# ❌ INCORRECT (ObjectNotExecutableError)
db.execute("SELECT NOW()")
```

### 5. Logging structuré ✅
```python
logger.info(f"🔐 Tentative de connexion pour: {login}")
logger.debug(f"   → Génération des tokens pour user_id={uid}")
logger.error(f"❌ Erreur: {e}", exc_info=True)
```

---

## 🚀 Commandes utiles

### Docker / PostgreSQL
```bash
# Démarrer
docker-compose up -d postgres

# Shell PostgreSQL
docker exec -it bcraftd-postgres psql -U bcraftd_user -d bcraftd

# Requêtes utiles
SELECT COUNT(*) FROM users;
SELECT * FROM refresh_tokens WHERE expires_at > NOW();
\dt  # Liste tables
\d+ users  # Structure détaillée
```

### Développement
```bash
# Lancer l'app
cd app
uvicorn main:app --reload --port 5000

# Tests
pytest tests/ -v
pytest tests/test_auth_flow.py -v -s

# Coverage
pytest --cov=app --cov-report=html
```

### Cleanup tokens (cron)
```bash
# Manuel
cd app
python -m scripts.cleanup_expired_tokens

# Crontab (toutes les heures)
0 * * * * cd /app && python -m scripts.cleanup_expired_tokens
```

---

## 📝 Tests de validation Auth

### Test 1: Login complet
```bash
curl -X POST http://localhost:5000/api/public/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "Test123!",
    "device_id": "laptop",
    "device_name": "MacBook Pro"
  }'

# Vérifier dans PostgreSQL
SELECT * FROM refresh_tokens WHERE user_id = '<user_id>';
```

### Test 2: Refresh (rotation)
```bash
curl -X POST http://localhost:5000/api/public/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<old_token>"}'

# Vérifier que l'ancien token a été supprimé
# et le nouveau créé
```

### Test 3: Logout all
```bash
curl -X POST http://localhost:5000/api/public/auth/logout_all \
  -H "Authorization: Bearer <access_token>"

# Vérifier que tous les tokens ont été supprimés
SELECT COUNT(*) FROM refresh_tokens WHERE user_id = '<user_id>';
# Devrait retourner 0
```

---

## 🎯 Plan de migration - Phase suivante

### Phase 1: Services métier (Jour 1)
**Objectif:** Adapter les services pour PostgreSQL

**Fichiers:**
1. `services/inventory_service.py`
   - Ajouter `db: Session` à toutes les fonctions
   - Remplacer `load_users/save_users` par `db.commit()`
   
2. `services/crafting_service.py`
   - Idem + validation avec `resource_crud.get(db, id)`
   - Vérifier niveau requis pour craft

**Pattern de migration:**
```python
# AVANT
def add_item(user: User, item: str, qty: int):
    user.inventory[item] = user.inventory.get(item, 0) + qty
    users = load_users()
    users[user.id] = user.to_dict()
    save_users(users)

# APRÈS
def add_item(db: Session, user: User, item: str, qty: int):
    user.inventory[item] = user.inventory.get(item, 0) + qty
    db.commit()
    db.refresh(user)
```

### Phase 2: Routes User métier (Jour 2)
**Objectif:** Fonctionnalités core du jeu

**Ordre:**
1. `routes/api/user/inventory.py` (add/remove/clear)
2. `routes/api/user/crafting.py` (possible/craft)
3. `routes/api/user/stats.py` (get/add_xp)

**Dépendances:** Services migrés en Phase 1

### Phase 3: Routes Admin + Loot (Jour 3)
**Objectif:** Administration complète

**Ordre:**
1. `routes/api/admin/users.py` (CRUD + grant_xp)
2. `routes/api/admin/settings.py` (feature flags)
3. `routes/api/admin/loot.py` + `routes/api/user/loot.py`
4. `routes/api/public/quests.py` + `routes/api/user/quests.py`

### Phase 4: Tests (Jour 4)
**Objectif:** Validation complète

**Fichiers à adapter:**
- `tests/conftest.py` - Fixtures avec PostgreSQL
- `tests/test_auth_flow.py` - ✅ À adapter pour PostgreSQL
- `tests/test_crafting.py` - À adapter
- `tests/test_inventory.py` - À adapter
- `tests/test_integration.py` - Nouveau (crafting → XP → level up)

### Phase 5: Cleanup (Jour 5)
**Objectif:** Supprimer code legacy

**Fichiers à supprimer:**
- `utils/crud.py`, `utils/json.py`
- `utils/local_api_dispatcher.py`, `utils/client.py`
- `database/database.py`
- `storage/*.json` (après validation complète)

---

## 🐛 Problèmes connus & solutions

### 1. Import models échoue
**Erreur:** `ModuleNotFoundError: No module named 'database.models'`

**Solution:** Vérifier structure des dossiers
```
database/
├── models/
│   ├── __init__.py  # ✅ Doit exister
│   └── user.py
```

### 2. ObjectNotExecutableError
**Erreur:** `Not an executable object: 'SELECT 1'`

**Solution:** Toujours utiliser `text()`
```python
from sqlalchemy import text
db.execute(text("SELECT 1"))
```

### 3. Tokens pas révoqués
**Cause:** Transaction non commitée

**Solution:** Toujours appeler `db.commit()`
```python
db.query(RefreshToken).filter(...).delete()
db.commit()  # ✅ Nécessaire
```

---

## 📋 Structure des fichiers actuelle

```
app/
├── database/
│   ├── connection.py ✅
│   ├── models/
│   │   ├── __init__.py ✅
│   │   ├── user.py ✅
│   │   ├── profession.py ✅
│   │   ├── resource.py ✅
│   │   ├── recipe.py ✅
│   │   └── refresh_token.py ✅
│   └── database.py ⚠️ À supprimer (ancien)
├── schemas/
│   ├── profession.py ✅
│   ├── resource.py ✅
│   ├── recipe.py ✅
│   └── user.py ✅
├── routes/
│   ├── api/
│   │   ├── admin/
│   │   │   ├── professions.py ✅
│   │   │   ├── resources.py ✅
│   │   │   ├── recipes.py ✅
│   │   │   ├── users.py ⏸️
│   │   │   ├── loot.py ⏸️
│   │   │   ├── settings.py ⏸️
│   │   │   └── dispatcher.py ⚠️ À supprimer
│   │   ├── public/
│   │   │   ├── auth.py ✅
│   │   │   ├── professions.py ✅
│   │   │   ├── resources.py ✅
│   │   │   ├── recipes.py ✅
│   │   │   └── quests.py ⏸️
│   │   └── user/
│   │       ├── me.py ✅
│   │       ├── professions.py ✅
│   │       ├── resources.py ✅
│   │       ├── recipes.py ✅
│   │       ├── inventory.py ⏸️
│   │       ├── crafting.py ⏸️
│   │       ├── stats.py ⏸️
│   │       └── loot.py ⏸️
├── services/
│   ├── xp_service.py ✅
│   ├── inventory_service.py ⏸️
│   └── crafting_service.py ⏸️
├── utils/
│   ├── auth.py ✅ (PostgreSQL)
│   ├── db_crud.py ✅
│   ├── deps.py ✅
│   ├── roles.py ✅
│   ├── crud.py ⚠️ À supprimer
│   ├── json.py ⚠️ À supprimer
│   ├── local_api_dispatcher.py ⚠️ À supprimer
│   └── client.py ⚠️ À supprimer
└── scripts/
    ├── migrate_json_to_postgres.py ✅
    └── cleanup_expired_tokens.py ✅
```

---

## 🎯 Prompt de reprise (nouvelle conversation)

```
Contexte: Migration PostgreSQL de B-CraftD (API FastAPI jeu de crafting)

État: CHECKPOINT V3 - Authentification PostgreSQL complète

TERMINÉ (60%):
- ✅ Infrastructure PostgreSQL fonctionnelle
- ✅ Modèles SQLAlchemy modulaires (database/models/)
- ✅ Données migrées avec succès
- ✅ Schémas Pydantic (profession, resource, recipe, user)
- ✅ AUTHENTIFICATION PostgreSQL COMPLÈTE 🎉
  - utils/auth.py refactorisé (store/revoke/rotate tokens)
  - routes/api/public/auth.py migré (login/refresh/logout)
  - Table refresh_tokens utilisée
  - Plus aucun JSON pour l'auth
- ✅ Routes migrées (46%):
  - Admin: professions, resources, recipes
  - Public: auth, professions, resources, recipes (100%)
  - User: me, professions, resources, recipes

PROCHAINE PRIORITÉ: Migrer services métier + routes User
1. services/inventory_service.py (ajouter db: Session)
2. services/crafting_service.py (ajouter db: Session)
3. routes/api/user/inventory.py
4. routes/api/user/crafting.py
5. routes/api/user/stats.py

IMPORTANT - Patch SQLAlchemy:
```python
from sqlalchemy import text
db.execute(text("SELECT 1"))  # ✅
db.execute("SELECT 1")  # ❌ ObjectNotExecutableError
```

Question: Par quel service veux-tu commencer?
(inventory_service ou crafting_service)
```

---

**Checkpoint créé:** 2025-01-15  
**Version:** 3.0  
**Prochain checkpoint:** Après migration services + routes User métier
