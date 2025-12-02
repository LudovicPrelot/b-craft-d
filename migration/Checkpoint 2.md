# 📚 Document de reprise - Migration PostgreSQL B-CraftD v2

**Dernière mise à jour:** [Date actuelle]  
**Version:** 2.0  
**Progression:** ~45%

---

## 🎯 État actuel (Checkpoint v2)

### ✅ Complètement terminé

#### 1. Infrastructure PostgreSQL
- ✅ Docker Compose avec service postgres
- ✅ Connexion testée et fonctionnelle
- ✅ Variables d'environnement configurées
- ✅ Patch SQLAlchemy mémorisé (`text()` pour SQL brut)

#### 2. Architecture modulaire des modèles
- ✅ **Réorganisation complète** : `database/models/` avec fichiers séparés
  - `user.py`
  - `profession.py`
  - `resource.py`
  - `recipe.py`
  - `refresh_token.py`
  - `__init__.py` (import centralisé)
- ✅ Suppression de l'ancien `database/models.py` monolithique
- ✅ Avantage : Chargement sélectif des modèles (performances)

#### 3. Migration des données
- ✅ Script `scripts/migrate_json_to_postgres.py` exécuté
- ✅ Toutes les données JSON transférées vers PostgreSQL
- ✅ Fichiers JSON conservés en backup dans `storage/`

#### 4. Utilitaires CRUD
- ✅ `utils/db_crud.py` créé avec `CRUDBase` générique
- ✅ Instances préconfigurées : `user_crud`, `profession_crud`, `resource_crud`, `recipe_crud`, `refresh_token_crud`

#### 5. Schémas Pydantic créés
- ✅ `schemas/profession.py` (ProfessionCreate, ProfessionUpdate, ProfessionResponse)
- ✅ `schemas/resource.py` (ResourceCreate, ResourceUpdate, ResourceResponse)
- ✅ `schemas/recipe.py` (RecipeCreate, RecipeUpdate, RecipeResponse)
- ✅ `schemas/user.py` (UserCreate, UserUpdate, UserResponse, UserProfileResponse)

#### 6. Routes migrées vers PostgreSQL

**Admin (4/7)**
- ✅ `routes/api/admin/professions.py` (avec validation métier)
- ✅ `routes/api/admin/resources.py` (avec recherche et stats)
- ✅ `routes/api/admin/recipes.py` (avec validation d'intégrité)
- ⏸️ `routes/api/admin/users.py` (reste à faire)
- ⏸️ `routes/api/admin/loot.py` (reste à faire)
- ⏸️ `routes/api/admin/settings.py` (reste à faire)
- ⏸️ `routes/api/admin/dispatcher.py` (peut être supprimé)

**Public (3/3)** ✅
- ✅ `routes/api/public/professions.py` (lecture seule)
- ✅ `routes/api/public/resources.py` (lecture seule)
- ✅ `routes/api/public/recipes.py` (lecture seule)
- ⏸️ `routes/api/public/quests.py` (reste à faire)
- ⏸️ `routes/api/public/auth.py` (critique, reste à faire)

**User (4/10)**
- ✅ `routes/api/user/professions.py` (lecture)
- ✅ `routes/api/user/resources.py` (lecture)
- ✅ `routes/api/user/recipes.py` (lecture)
- ✅ `routes/api/user/me.py` (profil + devices)
- ⏸️ `routes/api/user/inventory.py` (reste à faire)
- ⏸️ `routes/api/user/crafting.py` (reste à faire)
- ⏸️ `routes/api/user/stats.py` (reste à faire)
- ⏸️ `routes/api/user/loot.py` (reste à faire)
- ⏸️ `routes/api/user/quests.py` (reste à faire)
- ⏸️ `routes/api/user/dashboard.py` (reste à faire)

---

## 🚧 En cours / Priorités

### Priorité CRITIQUE (bloquants)

#### 1. ⚠️ Authentification (routes/api/public/auth.py)
**Impact:** Sans cette route, impossible de se connecter
**Complexité:** HAUTE
**Fichiers concernés:**
- `routes/api/public/auth.py` (login, refresh, logout)
- `utils/auth.py` (migration vers table `refresh_tokens`)

**Actions requises:**
```python
# Migrer les fonctions dans utils/auth.py pour utiliser SQLAlchemy
# Au lieu de load_json(REFRESH_TOKENS_FILE)
# Utiliser db.query(RefreshToken)...
```

#### 2. ⚠️ Routes User métier (inventory, crafting, stats)
**Impact:** Fonctionnalités core du jeu
**Complexité:** MOYENNE-HAUTE
**Fichiers:**
- `routes/api/user/inventory.py` (add/remove items)
- `routes/api/user/crafting.py` (craft avec validation)
- `routes/api/user/stats.py` (XP, level up)

**Prérequis:** Migrer les services métier d'abord

#### 3. ⚠️ Services métier
**Impact:** Logique business réutilisable
**Complexité:** MOYENNE
**Fichiers à migrer:**
- `services/crafting_service.py` (utiliser SQLAlchemy au lieu de JSON)
- `services/inventory_service.py` (idem)
- `services/xp_service.py` (OK, aucun stockage)

---

## 📋 Plan de migration détaillé (mis à jour)

### Phase 1: ✅ TERMINÉE (Infrastructure + Routes lecture seule)
- ✅ Setup PostgreSQL
- ✅ Modèles SQLAlchemy modulaires
- ✅ Migration des données
- ✅ Routes Admin (professions, resources, recipes)
- ✅ Routes Public (professions, resources, recipes)
- ✅ Routes User lecture (professions, resources, recipes, me)

### Phase 2: 🔥 EN COURS (Authentification + Services)
**Durée estimée:** 2-3 jours

1. **Auth (CRITIQUE)**
   - Migrer `utils/auth.py` vers PostgreSQL
   - Adapter `routes/api/public/auth.py`
   - Tester login/refresh/logout complet

2. **Services métier**
   - Adapter `services/crafting_service.py`
   - Adapter `services/inventory_service.py`
   - Garder `services/xp_service.py` tel quel

3. **Routes User métier**
   - `routes/api/user/inventory.py`
   - `routes/api/user/crafting.py`
   - `routes/api/user/stats.py`

### Phase 3: 🔜 À VENIR (Routes complexes)
**Durée estimée:** 2 jours

1. **Admin users**
   - `routes/api/admin/users.py` (CRUD + grant_xp)

2. **Loot system**
   - `routes/api/admin/loot.py` (tables de loot)
   - `routes/api/user/loot.py` (collecte)

3. **Quests**
   - `routes/api/public/quests.py` (liste)
   - `routes/api/user/quests.py` (completion)

4. **Settings**
   - `routes/api/admin/settings.py` (feature flags)

### Phase 4: 🧪 Tests (1 jour)
- Adapter fixtures pytest pour PostgreSQL
- Créer DB de test isolée
- Mettre à jour tous les tests existants

### Phase 5: 🧹 Cleanup final (2h)
- ✅ Supprimer `database/models.py` (remplacé par models/)
- Supprimer `utils/crud.py` (remplacé par db_crud.py)
- Supprimer `utils/json.py` (plus nécessaire)
- Supprimer `utils/local_api_dispatcher.py` (over-engineering)
- Supprimer `utils/client.py` (utiliser TestClient)
- Supprimer `database/database.py` (ancien système)
- Supprimer fichiers JSON après validation complète

---

## 🔧 Patch SQLAlchemy mémorisé

**IMPORTANT:** Depuis SQLAlchemy 2.0, toutes les requêtes SQL brutes doivent être wrappées avec `text()`

```python
from sqlalchemy import text  # ✅ Import nécessaire

# ❌ INCORRECT (provoque ObjectNotExecutableError)
conn.execute("SELECT 1")

# ✅ CORRECT
conn.execute(text("SELECT 1"))

# Exemples d'utilisation
db.query(User).filter(text("created_at > NOW() - INTERVAL '7 days'")).all()
db.execute(text("SELECT COUNT(*) FROM users WHERE level > :level"), {"level": 10})
```

**Source:** https://techoverflow.net/2024/07/06/how-to-fix-sqlalchemy-exc-objectnotexecutableerror-not-an-executable-object/

---

## 📊 Métriques de progression

### Avancement global: ~45%
- ✅ Infrastructure: 100%
- ✅ Modèles modulaires: 100%
- ✅ Migration données: 100%
- ✅ Schémas Pydantic: 50% (4/8 entités)
- ⏸️ Routes API: 45% (11/24)
  - Admin: 57% (4/7)
  - Public: 75% (3/4)
  - User: 40% (4/10)
- ⏸️ Services: 10% (xp_service OK, autres à migrer)
- ⏸️ Auth migration: 0%
- ⏸️ Tests: 0%
- ⏸️ Cleanup: 20%

### Temps estimé restant: 4-5 jours
- Auth + Services: 2 jours
- Routes complexes (loot, quests, users): 2 jours
- Tests: 1 jour
- Cleanup + validation: quelques heures

---

## 🎓 Nouvelles bonnes pratiques identifiées

### 1. Architecture modulaire des modèles ✅
**Avant:**
```python
# database/models.py - 300 lignes, tout chargé
from database.models import User, Profession, Resource, ...
```

**Après:**
```python
# database/models/user.py - 50 lignes
# database/models/profession.py - 30 lignes
# Import sélectif
from database.models import User  # Charge uniquement User
```

**Avantages:**
- Performances: charge uniquement les modèles nécessaires
- Maintenance: fichiers plus petits et focalisés
- Lisibilité: séparation claire des responsabilités

### 2. Validation Pydantic systématique ✅
**Toujours créer 3 schémas par entité:**
- `EntityCreate` (avec tous les champs requis)
- `EntityUpdate` (tous optionnels avec `exclude_unset=True`)
- `EntityResponse` (avec `from_attributes = True`)

### 3. Validation métier dans les routes ✅
**Exemple dans recipes.py:**
```python
# Vérifie que la profession existe avant de créer la recette
profession = profession_crud.get(db, recipe.required_profession)
if not profession:
    raise HTTPException(400, f"Profession not found")
```

### 4. Utilisation de `text()` pour SQL brut ✅
**Toujours wrapper les requêtes SQL:**
```python
from sqlalchemy import text
db.execute(text("SELECT NOW()"))
```

---

## 🚀 Commandes utiles

### Docker
```bash
# Démarrer PostgreSQL
docker-compose up -d postgres

# Logs
docker-compose logs -f postgres

# Shell PostgreSQL
docker exec -it bcraftd-postgres psql -U bcraftd_user -d bcraftd

# Requêtes SQL utiles
SELECT COUNT(*) FROM users;
SELECT * FROM professions;
SELECT table_name FROM information_schema.tables WHERE table_schema='public';
\dt  # Liste les tables
\d users  # Structure de la table users
```

### Développement
```bash
# Lancer l'app en dev
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Tests
pytest tests/ -v
pytest tests/test_auth_flow.py::test_login_success -v -s

# Coverage (à installer)
pip install pytest-cov
pytest --cov=app --cov-report=html
```

### Vérification des routes
```bash
# Ouvrir la doc interactive
http://localhost:5000/docs

# Tester une route manuellement
curl http://localhost:5000/api/public/professions
```

---

## 🎯 Prochaines étapes immédiates

### Option A: Continuer les routes User
1. Migrer `services/inventory_service.py`
2. Migrer `routes/api/user/inventory.py`
3. Tester add/remove items

### Option B: Débloquer l'auth (CRITIQUE)
1. Migrer `utils/auth.py` vers PostgreSQL
2. Adapter `routes/api/public/auth.py`
3. Tester login complet

### Option C: Finir les routes Admin
1. Migrer `routes/api/admin/users.py`
2. Migrer `routes/api/admin/loot.py`
3. Migrer `routes/api/admin/settings.py`

**Recommandation:** Option B (Auth) car c'est bloquant pour tout le reste.

---

## 📝 Notes importantes

### Conservation des JSON
Les fichiers JSON sont conservés en backup dans `storage/` jusqu'à validation complète. **Ne pas supprimer avant:**
- ✅ Toutes les routes migrées
- ✅ Tous les tests passent
- ✅ Validation en production pendant 1 semaine

### Structure des fichiers actuels
```
app/
├── database/
│   ├── connection.py ✅
│   ├── models/ ✅ NOUVEAU (modulaire)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── profession.py
│   │   ├── resource.py
│   │   ├── recipe.py
│   │   └── refresh_token.py
│   └── models.py ⚠️ À SUPPRIMER (ancien monolithique)
├── schemas/ ✅ NOUVEAU
│   ├── profession.py
│   ├── resource.py
│   ├── recipe.py
│   └── user.py
├── routes/
│   ├── api/
│   │   ├── admin/
│   │   │   ├── professions.py ✅
│   │   │   ├── resources.py ✅
│   │   │   ├── recipes.py ✅
│   │   │   ├── users.py ⏸️
│   │   │   ├── loot.py ⏸️
│   │   │   └── settings.py ⏸️
│   │   ├── public/
│   │   │   ├── professions.py ✅
│   │   │   ├── resources.py ✅
│   │   │   ├── recipes.py ✅
│   │   │   ├── auth.py ⚠️ CRITIQUE
│   │   │   └── quests.py ⏸️
│   │   └── user/
│   │       ├── professions.py ✅
│   │       ├── resources.py ✅
│   │       ├── recipes.py ✅
│   │       ├── me.py ✅
│   │       ├── inventory.py ⏸️
│   │       ├── crafting.py ⏸️
│   │       ├── stats.py ⏸️
│   │       └── loot.py ⏸️
├── services/
│   ├── crafting_service.py ⏸️ À migrer
│   ├── inventory_service.py ⏸️ À migrer
│   └── xp_service.py ✅ OK (pas de stockage)
└── utils/
    ├── db_crud.py ✅
    ├── crud.py ⚠️ À supprimer
    ├── json.py ⚠️ À supprimer
    ├── auth.py ⚠️ À migrer (critique)
    ├── local_api_dispatcher.py ⚠️ À supprimer
    └── client.py ⚠️ À supprimer
```

---

## 🎯 Prompt de reprise pour nouvelle conversation

```
Contexte: Je travaille sur B-CraftD, une API FastAPI de jeu de crafting.
Migration JSON → PostgreSQL en cours.

État actuel (v2):
- ✅ Infrastructure PostgreSQL fonctionnelle
- ✅ Modèles SQLAlchemy MODULAIRES (database/models/ avec fichiers séparés)
- ✅ Données migrées avec succès
- ✅ Schémas Pydantic créés (profession, resource, recipe, user)
- ✅ Routes migrées (45%):
  - Admin: professions, resources, recipes ✅
  - Public: professions, resources, recipes ✅
  - User: professions, resources, recipes, me ✅

Prochaine priorité CRITIQUE: Migration de l'authentification
- Migrer utils/auth.py pour utiliser table refresh_tokens (PostgreSQL)
- Adapter routes/api/public/auth.py (login, refresh, logout)

Note IMPORTANTE: Patch SQLAlchemy - Toujours utiliser text() pour SQL brut:
```python
from sqlalchemy import text
conn.execute(text("SELECT 1"))  # ✅
conn.execute("SELECT 1")  # ❌ ObjectNotExecutableError
```

Question: Par quelle partie de l'auth veux-tu commencer?
(Option: utils/auth.py ou routes/api/public/auth.py)
```

---

**Document mis à jour:** [Date]  
**Version:** 2.0  
**Prochain checkpoint:** Après migration complète de l'auth
