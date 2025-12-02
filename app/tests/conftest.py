# tests/conftest.py
"""
Fixtures pytest pour tests avec PostgreSQL.

Utilise une base de données de test isolée avec transactions rollback.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
import os

from database.connection import Base
from models import User, Profession, Resource, Recipe
from main import app
from utils.auth import hash_password
from utils.db_crud import user_crud, profession_crud, resource_crud, recipe_crud


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_db_url():
    """
    URL de la base de données de test.
    
    Utilise une DB séparée pour les tests.
    """
    # Utilise la DB de test depuis .env ou créer une DB test
    base_url = os.getenv("DATABASE_URL", "postgresql://bcraftd_user:bcraftd_password@localhost:5432")
    test_db_name = "bcraftd_test"
    
    # Remplace le nom de la DB par la DB de test
    if base_url.endswith("/bcraftd"):
        return base_url.replace("/bcraftd", f"/{test_db_name}")
    return f"{base_url}/{test_db_name}"


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """
    Crée un engine SQLAlchemy pour les tests.
    
    Scope: session (réutilisé pour tous les tests)
    """
    engine = create_engine(
        test_db_url,
        echo=False,  # Pas de logs SQL pendant les tests
        pool_pre_ping=True,
    )
    
    # Vérifie la connexion
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.exit(f"❌ Impossible de se connecter à la DB de test: {e}")
    
    # Crée toutes les tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup: supprime toutes les tables après les tests
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """
    Crée une session DB pour chaque test avec transaction rollback.
    
    Scope: function (nouvelle session par test)
    
    Chaque test s'exécute dans une transaction qui est rollback à la fin,
    garantissant l'isolation complète entre les tests.
    """
    # Crée une connexion
    connection = test_engine.connect()
    
    # Démarre une transaction
    transaction = connection.begin()
    
    # Crée une session liée à cette transaction
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    
    yield session
    
    # Rollback de la transaction (annule tous les changements)
    session.close()
    transaction.rollback()
    connection.close()


# ============================================================================
# FASTAPI CLIENT FIXTURE
# ============================================================================

@pytest.fixture(scope="function")
def client(db_session):
    """
    TestClient FastAPI avec override de la DB pour utiliser db_session.
    
    Permet de tester les routes API avec rollback automatique.
    """
    from database.connection import get_db
    
    # Override la dépendance get_db pour utiliser notre session de test
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Ne pas fermer, géré par la fixture db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore la dépendance originale
    app.dependency_overrides.clear()


# ============================================================================
# DATA FIXTURES (Données de test réutilisables)
# ============================================================================

@pytest.fixture
def sample_profession(db_session):
    """Crée une profession de test."""
    profession = Profession(
        id="mineur",
        name="Mineur",
        description="Expert en extraction de minerais",
        resources_found=["argile", "calcaire", "fer"],
        allowed_recipes=["ciment"],
        subclasses=["foreur", "géologue"]
    )
    db_session.add(profession)
    db_session.commit()
    db_session.refresh(profession)
    return profession


@pytest.fixture
def sample_resource(db_session):
    """Crée une ressource de test."""
    resource = Resource(
        id="argile",
        name="Argile",
        type="mineral",
        description="Roche sédimentaire",
        weight=1.0,
        stack_size=999
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


@pytest.fixture
def sample_recipe(db_session, sample_profession, sample_resource):
    """Crée une recette de test (nécessite profession et resource)."""
    # Crée la ressource de sortie si elle n'existe pas
    output_resource = db_session.query(Resource).filter(Resource.id == "ciment").first()
    if not output_resource:
        output_resource = Resource(
            id="ciment",
            name="Ciment",
            type="material",
            description="Matériau de construction"
        )
        db_session.add(output_resource)
    
    # Crée les ressources ingrédients si elles n'existent pas
    calcaire = db_session.query(Resource).filter(Resource.id == "calcaire").first()
    if not calcaire:
        calcaire = Resource(
            id="calcaire",
            name="Calcaire",
            type="mineral"
        )
        db_session.add(calcaire)
    
    db_session.commit()
    
    recipe = Recipe(
        id="ciment",
        output="ciment",
        ingredients={"argile": 1, "calcaire": 1},
        required_profession="mineur",
        required_level=1,
        xp_reward=10
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe


@pytest.fixture
def sample_user(db_session, sample_profession):
    """Crée un utilisateur de test."""
    user = User(
        id="test-user-123",
        firstname="Test",
        lastname="User",
        mail="test@example.com",
        login="testuser",
        password_hash=hash_password("Test123!"),
        profession="mineur",
        inventory={"argile": 5, "calcaire": 3},
        xp=0,
        level=1,
        stats={"strength": 1, "agility": 1, "endurance": 1},
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Crée un utilisateur admin de test."""
    user = User(
        id="admin-user-123",
        firstname="Admin",
        lastname="User",
        mail="admin@example.com",
        login="admin",
        password_hash=hash_password("Admin123!"),
        is_admin=True,
        is_moderator=True,
        profession="",
        inventory={},
        xp=0,
        level=1,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============================================================================
# AUTH FIXTURES (Tokens)
# ============================================================================

@pytest.fixture
def user_token(client, sample_user):
    """
    Crée un token d'authentification pour un utilisateur standard.
    
    Returns:
        str: Access token valide
    """
    response = client.post("/api/public/auth/login", json={
        "login": sample_user.login,
        "password": "Test123!",
        "device_id": "test-device",
        "device_name": "Test Device"
    })
    
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    """
    Crée un token d'authentification pour un admin.
    
    Returns:
        str: Access token valide avec privilèges admin
    """
    response = client.post("/api/public/auth/login", json={
        "login": admin_user.login,
        "password": "Admin123!",
        "device_id": "admin-device",
        "device_name": "Admin Device"
    })
    
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    """
    Helper pour créer des headers d'authentification.
    
    Usage:
        response = client.get("/api/user/me", headers=auth_headers(user_token))
    """
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# MARKERS (pour catégoriser les tests)
# ============================================================================

def pytest_configure(config):
    """Configure les markers personnalisés."""
    config.addinivalue_line(
        "markers", "slow: marque les tests lents (> 1s)"
    )
    config.addinivalue_line(
        "markers", "integration: tests d'intégration complets"
    )
    config.addinivalue_line(
        "markers", "auth: tests d'authentification"
    )