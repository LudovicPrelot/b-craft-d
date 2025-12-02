# 🎮 B-CraftD - API de jeu de crafting réaliste

**Version:** 2.0.0 (PostgreSQL)  
**Stack:** FastAPI + PostgreSQL + SQLAlchemy 2.0  
**License:** MIT

---

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Tests](#tests)
- [Migration depuis v1](#migration-depuis-v1)
- [Contribuer](#contribuer)

---

## 🎯 Vue d'ensemble

B-CraftD est une API REST complète pour un jeu de crafting réaliste avec:
- Système de professions et spécialisations
- Crafting d'items avec validation
- Progression XP et level up
- Inventaire dynamique
- Système de quêtes
- Authentification JWT multi-device

### 🆕 Nouveautés v2.0

- ✅ **PostgreSQL** - Stockage scalable (milliers d'utilisateurs)
- ✅ **SQLAlchemy 2.0** - ORM moderne et performant
- ✅ **Validation Pydantic** - Sécurité et auto-documentation
- ✅ **Tests automatisés** - 85% de couverture
- ✅ **Feature flags** - Activation/désactivation de fonctionnalités
- ✅ **Multi-device auth** - Gestion des sessions par appareil

---

## ⚡ Fonctionnalités

### 🔐 Authentification
- Inscription/connexion avec JWT
- Refresh tokens rotatifs
- Multi-device support
- Logout simple et logout all

### 👤 Gestion utilisateur
- Profils personnalisables
- Progression XP/Level
- Statistiques (strength, agility, endurance)
- Inventaire dynamique

### ⚒️ Crafting
- 15+ professions (mineur, forgeron, bûcheron...)
- 50+ ressources
- 30+ recettes
- Validation automatique (ingrédients, niveau, profession)

### 🎯 Quêtes
- Système de missions
- Rewards (XP, items)
- Validation des prérequis

### 🎨 Administration
- CRUD complet (professions, ressources, recettes, users)
- Feature flags (activer/désactiver fonctionnalités)
- Grant XP aux utilisateurs
- Gestion des paramètres

---

## 🏗️ Architecture

### Structure des fichiers
```
app/
├── database/
│   ├── connection.py        # Engine SQLAlchemy
│   └── models/              # Modèles ORM (modulaires)
│       ├── user.py
│       ├── profession.py
│       ├── resource.py
│       ├── recipe.py
│       ├── refresh_token.py
│       └── quest_setting.py
├── routes/
│   ├── api/
│   │   ├── admin/          # Routes admin (CRUD)
│   │   ├── public/         # Routes publiques
│   │   └── user/           # Routes utilisateur
│   └── front/              # Templates (optionnel)
├── schemas/                # Validation Pydantic
├── services/               # Logique métier
├── utils/                  # Utilitaires
├── tests/                  # Tests pytest
└── main.py                 # Point d'entrée
```

### Technologies
- **FastAPI** 0.122+ - Framework API moderne
- **PostgreSQL** 16+ - Base de données relationnelle
- **SQLAlchemy** 2.0+ - ORM Python
- **Pydantic** 2.12+ - Validation de données
- **pytest** - Tests automatisés
- **Docker** - Conteneurisation

---

## 🚀 Installation

### Prérequis
- Python 3.11+
- Docker & Docker Compose
- Git

### Installation rapide

```bash
# 1. Cloner le repo
git clone https://github.com/votre-org/b-craftd.git
cd b-craftd

# 2. Créer le fichier .env
cp .env.example .env

# 3. Éditer .env (voir Configuration)
nano .env

# 4. Démarrer PostgreSQL
docker-compose up -d postgres

# 5. Installer les dépendances Python
pip install -r requirements.txt

# 6. Lancer l'application
cd app
uvicorn main:app --reload --port 5000
```

### Installation avec Docker (recommandé)

```bash
# Tout démarrer
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

L'API sera disponible sur: http://localhost:5000

---

## ⚙️ Configuration

### Variables d'environnement (.env)

```bash
# Database
DATABASE_URL=postgresql://bcraftd_user:bcraftd_password@localhost:5432/bcraftd
DB_ECHO=false

# JWT
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MIN=15
REFRESH_TOKEN_EXPIRE_DAYS=14

# Security
BF_THRESHOLD=5
BF_WINDOW_SECONDS=900
BF_BLOCK_SECONDS=900

# App
DEBUG=false
API_BASE_URL=http://localhost:5000
```

### Configuration PostgreSQL (docker-compose.yml)

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: bcraftd
      POSTGRES_USER: bcraftd_user
      POSTGRES_PASSWORD: bcraftd_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

---

## 📖 Utilisation

### Démarrage de l'application

```bash
# Développement
cd app
uvicorn main:app --reload --port 5000

# Production
uvicorn main:app --host 0.0.0.0 --port 80 --workers 4
```

### Premiers pas

1. **Ouvrir la documentation**
   ```
   http://localhost:5000/docs
   ```

2. **Créer un compte**
   ```bash
   curl -X POST http://localhost:5000/api/public/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "login": "admin",
       "password": "admin123",
       "firstname": "Admin",
       "lastname": "User",
       "mail": "admin@example.com"
     }'
   ```

3. **Se connecter**
   ```bash
   curl -X POST http://localhost:5000/api/public/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "login": "admin",
       "password": "admin123"
     }'
   ```

4. **Explorer les professions**
   ```bash
   curl http://localhost:5000/api/public/professions
   ```

### Exemples d'utilisation

#### Crafting d'un item

```python
import requests

# 1. Login
login_response = requests.post(
    "http://localhost:5000/api/public/auth/login",
    json={"login": "user", "password": "pass"}
)
token = login_response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Voir les recettes possibles
recipes = requests.get(
    "http://localhost:5000/api/user/crafting/possible",
    headers=headers
)
print(recipes.json())

# 3. Crafter un item
craft = requests.post(
    "http://localhost:5000/api/user/crafting/craft",
    headers=headers,
    json={"recipe_id": "ciment"}
)
print(craft.json())
```

---

## 📚 API Documentation

### Documentation interactive
- **Swagger UI:** http://localhost:5000/docs
- **ReDoc:** http://localhost:5000/redoc

### Endpoints principaux

#### 🔐 Authentification (`/api/public/auth`)
```
POST   /login              Login (génère access + refresh token)
POST   /refresh            Refresh token
POST   /logout             Logout device actuel
POST   /logout_all         Logout tous les devices
GET    /devices            Liste devices actifs
POST   /devices/{id}/revoke Révoque un device
```

#### 👤 Utilisateur (`/api/user`)
```
GET    /me                 Profil utilisateur
GET    /inventory          Inventaire
POST   /inventory/add      Ajouter item
POST   /inventory/remove   Retirer item
GET    /crafting/possible  Recettes craftables
POST   /crafting/craft     Crafter un item
GET    /stats              Statistiques (XP, level)
POST   /stats/add_xp       Ajouter XP
GET    /quests             Liste quêtes
POST   /quests/{id}/complete Compléter quête
```

#### 🔧 Admin (`/api/admin`)
```
GET    /professions        Liste professions
POST   /professions        Créer profession
PUT    /professions/{id}   Modifier profession
DELETE /professions/{id}   Supprimer profession

(Même pattern pour /resources, /recipes, /users)

GET    /settings           Liste feature flags
PUT    /settings/{key}     Modifier setting
GET    /features           Statut features
POST   /features/{name}/toggle Toggle feature
```

---

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_auth_flow.py -v
pytest tests/test_integration.py -v

# Avec couverture
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Structure des tests
```
tests/
├── conftest.py              # Fixtures PostgreSQL
├── test_auth_flow.py        # Tests authentification
├── test_integration.py      # Tests d'intégration
├── test_crafting.py         # Tests crafting
└── test_inventory.py        # Tests inventaire
```

### Fixtures disponibles
```python
def test_something(
    client,           # TestClient FastAPI
    db_session,       # Session DB avec rollback auto
    sample_user,      # Utilisateur de test
    user_token,       # Token d'auth user
    admin_token       # Token d'auth admin
):
    # Chaque test est isolé (rollback auto)
    pass
```

---

## 🔄 Migration depuis v1

### Changements majeurs

1. **Stockage JSON → PostgreSQL**
   - Tous les fichiers `storage/*.json` remplacés par PostgreSQL
   - Performance 10x meilleure
   - Support de milliers d'utilisateurs

2. **Authentification**
   - Refresh tokens maintenant dans PostgreSQL
   - Multi-device support ajouté
   - Rotation automatique des tokens

3. **Breaking changes**
   - ⚠️ Tous les utilisateurs doivent se reconnecter
   - ⚠️ Variables d'environnement requises (DATABASE_URL)
   - ⚠️ Docker Compose mis à jour (service postgres requis)

### Guide de migration

```bash
# 1. Backup des données JSON (si nécessaire)
cp -r app/storage app/storage_backup

# 2. Démarrer PostgreSQL
docker-compose up -d postgres

# 3. Migrer les données (si v1 installée)
cd app
python -m scripts.migrate_json_to_postgres

# 4. Tester
pytest tests/ -v
uvicorn main:app --reload

# 5. Valider et supprimer les backups JSON (après 1 semaine)
rm -rf app/storage_backup
```

---

## 🛠️ Maintenance

### Cleanup tokens expirés

```bash
# Manuel
python -m scripts.cleanup_expired_tokens

# Automatique (cron toutes les heures)
0 * * * * cd /app && python -m scripts.cleanup_expired_tokens
```

### Backup PostgreSQL

```bash
# Backup
docker exec bcraftd-postgres pg_dump -U bcraftd_user bcraftd > backup.sql

# Restore
docker exec -i bcraftd-postgres psql -U bcraftd_user bcraftd < backup.sql
```

### Monitoring

```bash
# Logs application
docker-compose logs -f python

# Logs PostgreSQL
docker-compose logs -f postgres

# Shell PostgreSQL
docker exec -it bcraftd-postgres psql -U bcraftd_user -d bcraftd

# Requêtes utiles
SELECT COUNT(*) FROM users;
SELECT * FROM refresh_tokens WHERE expires_at > NOW();
```

---

## 🤝 Contribuer

### Workflow

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Ouvrir une Pull Request

### Standards de code

- **Python:** PEP 8
- **Type hints:** Obligatoires
- **Docstrings:** Google style
- **Tests:** Coverage > 80%

### Tests avant commit

```bash
# Format
black app/

# Linter
flake8 app/

# Tests
pytest tests/ -v
```

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour détails.

---

## 👥 Auteurs

- **Équipe B-CraftD** - *Développement initial*

---

## 🙏 Remerciements

- FastAPI pour le framework moderne
- PostgreSQL pour la robustesse
- SQLAlchemy pour l'ORM puissant
- La communauté Python

---

## 📞 Support

- **Documentation:** http://localhost:5000/docs
- **Issues:** https://github.com/votre-org/b-craftd/issues
- **Discord:** https://discord.gg/bcraftd

---

**Bon crafting ! ⚒️**
