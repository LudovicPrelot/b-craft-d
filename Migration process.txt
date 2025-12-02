# 📚 Document de reprise - Migration PostgreSQL B-CraftD

## 🔧 Patch SQLAlchemy corrigé et mémorisé

### Problème rencontré
```python
# ❌ Code original qui provoque l'erreur
def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")  # ❌ String directe non exécutable
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
```

**Erreur:** `sqlalchemy.exc.ObjectNotExecutableError: Not an executable object: 'SELECT 1'`

### Solution (SQLAlchemy 2.0+)
```python
from sqlalchemy import text  # ✅ Import nécessaire

def check_db_connection() -> bool:
    """Vérifie que la DB est accessible."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # ✅ Wrap avec text()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
```

**Explication:** Depuis SQLAlchemy 2.0, toutes les requêtes SQL brutes doivent être wrappées avec `text()` pour des raisons de sécurité et de typage.

**Source:** https://techoverflow.net/2024/07/06/how-to-fix-sqlalchemy-exc-objectnotexecutableerror-not-an-executable-object/

---

## 📊 État actuel du projet (checkpoint)

### ✅ Réalisé
1. **Infrastructure PostgreSQL**
   - Docker Compose configuré avec service postgres
   - Connexion testée et fonctionnelle
   - Variables d'environnement configurées

2. **Modèles SQLAlchemy**
   - `database/connection.py` créé avec engine, session, Base
   - `database/models.py` créé avec tous les modèles (User, Profession, Resource, Recipe, etc.)
   - Tables créées dans PostgreSQL

3. **Migration des données**
   - Script `scripts/migrate_json_to_postgres.py` exécuté avec succès
   - Données JSON transférées vers PostgreSQL
   - Fichiers JSON conservés en backup

4. **Utilitaires CRUD**
   - `utils/db_crud.py` créé avec classe générique `CRUDBase`
   - Instances préconfigurées (`user_crud`, `profession_crud`, etc.)

### 🚧 En cours / À faire

1. **Refactoring des routes API** ⏳
   - ✅ Exemple fourni: `routes/api/admin/professions.py`
   - ⏸️ À migrer: 
     - `routes/api/admin/resources.py`
     - `routes/api/admin/recipes.py`
     - `routes/api/admin/users.py`
     - `routes/api/admin/loot.py`
     - `routes/api/public/*` (auth, professions, recipes, resources, quests)
     - `routes/api/user/*` (crafting, inventory, loot, me, stats, etc.)

2. **Schémas Pydantic** 📝
   - À créer: `schemas/` avec validation des request/response
   - Priorité: `profession.py`, `user.py`, `recipe.py`, `resource.py`

3. **Services métier** 🔧
   - Adapter `services/crafting_service.py` pour utiliser SQLAlchemy
   - Adapter `services/inventory_service.py`
   - Adapter `services/xp_service.py`

4. **Authentification** 🔐
   - Migrer `utils/auth.py` pour utiliser la table `refresh_tokens`
   - Mettre à jour `routes/api/public/auth.py`

5. **Tests** 🧪
   - Adapter les fixtures pytest pour utiliser PostgreSQL
   - Créer une DB de test isolée
   - Mettre à jour tous les tests existants

6. **Cleanup final** 🧹
   - Supprimer `utils/crud.py` (remplacé par `db_crud.py`)
   - Supprimer `utils/json.py` (plus nécessaire)
   - Supprimer `utils/local_api_dispatcher.py` (over-engineering)
   - Supprimer `utils/client.py` (utiliser TestClient)
   - Supprimer `database/database.py` (ancien système avec JSON)
   - Supprimer les fichiers JSON après validation complète

---

## 📋 Analyse complète du code (résumé)

### Points forts identifiés
- ✅ Architecture modulaire propre (API/Front séparé)
- ✅ Système de rôles bien implémenté
- ✅ JWT avec refresh tokens rotatifs (excellent!)
- ✅ Logging structuré et complet
- ✅ Validation d'intégrité des données au démarrage

### Problèmes critiques identifiés (par priorité)

#### 1. ✅ **RÉSOLU** - Stockage JSON → PostgreSQL
**Impact:** Scalabilité impossible au-delà de ~100 utilisateurs, race conditions, pas de transactions

**Solution appliquée:**
- Migration vers PostgreSQL avec SQLAlchemy
- Modèles ORM créés
- Données migrées avec succès

#### 2. ⏸️ **EN COURS** - Validation Pydantic inexistante
**Impact:** Pas de validation des données entrantes, erreurs runtime, mauvaise doc OpenAPI

**Solution:**
```python
# ❌ Actuel
@router.post("/")
def create_profession(payload: dict = Body(...)):
    pass

# ✅ À faire
from pydantic import BaseModel, Field

class ProfessionCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    name: str
    
@router.post("/", response_model=ProfessionResponse)
def create_profession(payload: ProfessionCreate):
    pass
```

**Action requise:** Créer `schemas/` avec tous les modèles Pydantic

#### 3. 🔜 **À FAIRE** - Dispatcher local = Over-engineering
**Impact:** 200 lignes de code inutiles, complexité de maintenance

**Solution:** Supprimer `local_api_dispatcher.py` et `client.py`, utiliser `TestClient` de FastAPI

```python
# Au lieu du dispatcher custom
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get("/api/public/professions")
```

#### 4. 🔜 **À FAIRE** - Services métier faibles
**Impact:** Pas de validation business (limites inventaire, poids, etc.)

**Exemple actuel:**
```python
# services/inventory_service.py - trop simple
def add_item(user: User, item: str, qty: int = 1):
    user.inventory[item] = user.inventory.get(item, 0) + qty
```

**À améliorer:**
```python
class InventoryService:
    MAX_STACK = 999
    MAX_WEIGHT = 1000
    
    def add_item(self, user: User, item_id: str, qty: int):
        # Validation ressource existe
        resource = resource_crud.get(db, item_id)
        if not resource:
            raise ItemNotFoundError()
        
        # Limite stack
        new_total = user.inventory.get(item_id, 0) + qty
        if new_total > self.MAX_STACK:
            raise InventoryFullError()
        
        # Calcul poids
        # ...
```

### Bugs potentiels identifiés

1. **Race condition sur refresh tokens** (sera résolu par PostgreSQL + transactions)
2. **Crafting sans vérification de niveau** (`services/crafting_service.py`)
3. **Device tracking cassé** (génère un UUID à chaque login si device_id absent)

---

## 🎯 Plan de migration détaillé (ordre recommandé)

### Phase 1: Routes Admin (2 jours)
```
Priorité: HAUTE
Complexité: MOYENNE

1. routes/api/admin/professions.py ✅ (exemple fourni)
2. routes/api/admin/resources.py
3. routes/api/admin/recipes.py
4. routes/api/admin/users.py
5. routes/api/admin/loot.py
6. routes/api/admin/settings.py
```

### Phase 2: Routes Public (1 jour)
```
Priorité: HAUTE
Complexité: MOYENNE

1. routes/api/public/professions.py
2. routes/api/public/resources.py
3. routes/api/public/recipes.py
4. routes/api/public/quests.py
```

### Phase 3: Authentification (1 jour)
```
Priorité: CRITIQUE
Complexité: HAUTE

1. Migrer utils/auth.py (table refresh_tokens)
2. Migrer routes/api/public/auth.py
3. Mettre à jour utils/deps.py si nécessaire
```

### Phase 4: Routes User (2 jours)
```
Priorité: HAUTE
Complexité: HAUTE (logique métier)

1. routes/api/user/me.py
2. routes/api/user/inventory.py
3. routes/api/user/crafting.py
4. routes/api/user/stats.py
5. routes/api/user/loot.py
6. routes/api/user/quests.py
7. routes/api/user/devices.py
```

### Phase 5: Services métier (1 jour)
```
Priorité: MOYENNE
Complexité: MOYENNE

1. services/crafting_service.py
2. services/inventory_service.py
3. services/xp_service.py
4. services/professions_service.py (peut être supprimé, remplacé par db_crud)
5. services/recipes_service.py (idem)
6. services/resources_service.py (idem)
```

### Phase 6: Schémas Pydantic (1 jour)
```
Priorité: HAUTE
Complexité: FAIBLE

Créer schemas/:
- profession.py
- resource.py
- recipe.py
- user.py
- auth.py
- crafting.py
- inventory.py
- loot.py
- quest.py
```

### Phase 7: Tests (1 jour)
```
Priorité: HAUTE
Complexité: MOYENNE

1. Créer conftest.py avec fixtures DB
2. Adapter test_auth_flow.py
3. Adapter test_crafting.py
4. Adapter test_inventory.py
5. Créer test_integration.py
```

### Phase 8: Cleanup (2h)
```
Priorité: FAIBLE
Complexité: FAIBLE

Supprimer:
- utils/crud.py
- utils/json.py
- utils/local_api_dispatcher.py
- utils/client.py
- database/database.py (ancien)
- generated/
- scripts/fix_bugs.py
- storage/*.json (après validation complète)
```

---

## 📖 Template de migration pour une route

Voici le template à suivre pour chaque route :

```python
# AVANT (JSON)
from fastapi import APIRouter, Body
from utils.roles import require_admin
from utils.crud import list_all, get_one, create_one, update_one, delete_one
import config

router = APIRouter(prefix="/resources", tags=["Admin - Resources"])

@router.get("/")
def list_resources():
    return list_all(config.RESOURCES_FILE, "resources", logger)

@router.post("/")
def create_resource(payload: dict = Body(...)):
    return create_one(config.RESOURCES_FILE, payload, "resource", logger)

# APRÈS (PostgreSQL)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from utils.roles import require_admin
from utils.db_crud import resource_crud
from database.connection import get_db
from schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse

router = APIRouter(prefix="/resources", tags=["Admin - Resources"])

@router.get("/", response_model=List[ResourceResponse])
def list_resources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return resource_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=ResourceResponse, status_code=201)
def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db)
):
    return resource_crud.create(db, obj_in=resource.model_dump())
```

**Checklist par route:**
- [ ] Remplacer `dict` par schéma Pydantic
- [ ] Ajouter `db: Session = Depends(get_db)`
- [ ] Utiliser `{entity}_crud` au lieu de `load_json/save_json`
- [ ] Ajouter `response_model` pour auto-documentation
- [ ] Gérer les transactions (commit automatique avec CRUD)
- [ ] Tester la route avec `/docs`

---

## 🚀 Commandes utiles

### Docker
```bash
# Démarrer PostgreSQL
docker-compose up -d postgres

# Vérifier les logs
docker-compose logs -f postgres

# Shell PostgreSQL
docker exec -it bcraftd-postgres psql -U bcraftd_user -d bcraftd

# Requêtes SQL utiles
SELECT COUNT(*) FROM users;
SELECT * FROM professions;
SELECT table_name FROM information_schema.tables WHERE table_schema='public';
```

### Migration
```bash
# Lancer la migration (déjà fait)
cd app
python -m scripts.migrate_json_to_postgres

# Backup JSON
cp -r app/storage app/storage_backup_$(date +%Y%m%d)
```

### Développement
```bash
# Lancer l'app en dev
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Tests
pytest tests/ -v
pytest tests/test_auth_flow.py -v -s
```

### Alembic (migrations de schéma - optionnel)
```bash
# Initialiser Alembic
alembic init alembic

# Créer une migration
alembic revision --autogenerate -m "Add column X to users"

# Appliquer les migrations
alembic upgrade head
```

---

## 🐛 Problèmes connus et solutions

### 1. Token JWT invalide après migration
**Cause:** Les refresh tokens ont été migrés avec leurs hashes, mais les tokens JWT originaux ne sont plus valides

**Solution:** Forcer une reconnexion de tous les utilisateurs ou régénérer les tokens

### 2. Inventaires vides après migration
**Cause:** Le champ `inventory` JSON peut être `null` au lieu de `{}`

**Solution:** Ajouter un default dans le modèle
```python
inventory = Column(JSON, default=dict, nullable=False)
```

### 3. Erreur "relation does not exist"
**Cause:** Les tables n'ont pas été créées

**Solution:**
```python
# Dans main.py ou script de migration
from database.connection import init_db
init_db()
```

---

## 📝 Notes importantes

### Conservation des JSON
Les fichiers JSON sont conservés en backup dans `storage/` jusqu'à validation complète du système PostgreSQL. Ne pas les supprimer avant d'avoir :
- ✅ Migré toutes les routes
- ✅ Testé toutes les fonctionnalités
- ✅ Validé en production pendant 1 semaine

### Performance PostgreSQL
Avec PostgreSQL, on peut maintenant :
- Gérer des milliers d'utilisateurs concurrents
- Faire des requêtes complexes (JOIN, agrégations)
- Utiliser des transactions ACID
- Indexer pour des performances optimales

### Prochaines optimisations post-migration
Une fois la migration terminée, on pourra :
1. Ajouter un cache Redis pour les données statiques (professions, recipes)
2. Implémenter des relations SQLAlchemy (User.profession → ForeignKey)
3. Ajouter des full-text search sur les descriptions
4. Optimiser avec des index composites pour les requêtes fréquentes

---

## 🎯 Reprise de conversation - Prompt suggéré

Voici le prompt à utiliser pour reprendre dans une nouvelle conversation :

```
Contexte: Je travaille sur B-CraftD, une API FastAPI de jeu de crafting. 
Nous sommes en train de migrer du stockage JSON vers PostgreSQL.

État actuel:
- ✅ Infrastructure PostgreSQL configurée et fonctionnelle
- ✅ Modèles SQLAlchemy créés (database/models.py)
- ✅ Données JSON migrées vers PostgreSQL avec succès
- ✅ Utilitaires CRUD créés (utils/db_crud.py)
- ✅ Exemple de route migrée: routes/api/admin/professions.py

Prochaine étape: Migrer les routes API restantes en suivant le plan de migration.

Ordre de priorité:
1. Routes admin (resources, recipes, users, loot, settings)
2. Routes public (professions, resources, recipes, quests)
3. Authentification (auth.py avec refresh tokens PostgreSQL)
4. Routes user (inventory, crafting, stats, loot, quests, me)
5. Services métier (crafting_service, inventory_service, xp_service)
6. Schémas Pydantic (création du dossier schemas/)
7. Tests (adaptation des fixtures pour PostgreSQL)
8. Cleanup final (suppression des anciens fichiers)

Note importante: Patch SQLAlchemy mémorisé - Toujours utiliser `text()` 
pour les requêtes SQL brutes:
```python
from sqlalchemy import text
conn.execute(text("SELECT 1"))  # ✅ Correct
conn.execute("SELECT 1")  # ❌ Provoque ObjectNotExecutableError
```

Question: Par quelle route veux-tu commencer la migration?
```

---

## 📊 Métriques de progression

### Avancement global: ~20%
- ✅ Infrastructure: 100%
- ✅ Modèles: 100%
- ✅ Migration données: 100%
- ⏸️ Routes API: 5% (1/20)
- ⏸️ Services: 0%
- ⏸️ Schémas Pydantic: 0%
- ⏸️ Tests: 0%
- ⏸️ Cleanup: 0%

### Temps estimé restant: 7-8 jours
- Routes API: 4 jours
- Services + Schémas: 2 jours
- Tests: 1 jour
- Cleanup + validation: 1 jour

---

**Document créé le:** [Date actuelle]  
**Version:** 1.0  
**Auteur:** Assistant Claude  
**Projet:** B-CraftD Migration PostgreSQL