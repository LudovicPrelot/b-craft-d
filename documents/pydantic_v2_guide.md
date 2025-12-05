# 📘 Pydantic v2 Migration Guide - B-CraftD v3.0

**Date** : 4 décembre 2025  
**Version Pydantic** : 2.12.5  
**Statut** : 🔴 OBLIGATOIRE pour tous les schémas

---

## 🎯 Règle Critique : Migration Config → model_config

### ❌ ANCIEN (Pydantic v1.x)

```python
from pydantic import BaseModel, Field

class RecipeCreate(RecipeBase):
    """Schéma pour la création d'une recette."""
    id: str = Field(..., min_length=1, max_length=50, description="Identifiant unique")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ciment",
                "output": "ciment",
                "ingredients": {
                    "argile": 1,
                    "calcaire": 1
                },
                "required_profession": "mineur",
                "required_level": 1,
                "xp_reward": 10
            }
        }
```

### ✅ NOUVEAU (Pydantic v2.12.5)

```python
from pydantic import BaseModel, Field, ConfigDict

class RecipeCreate(RecipeBase):
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "id": "ciment",
                "output": "ciment",
                "ingredients": {
                    "argile": 1,
                    "calcaire": 1
                },
                "required_profession": "mineur",
                "required_level": 1,
                "xp_reward": 10
            }
        }
    )
    
    """Schéma pour la création d'une recette."""
    id: str = Field(..., min_length=1, max_length=50, description="Identifiant unique")
```

---

## 📋 Changements Principaux Pydantic v2

### 1. Configuration de Modèle

| Aspect | Pydantic v1 | Pydantic v2 |
|--------|-------------|-------------|
| **Import** | `from pydantic import BaseModel` | `from pydantic import BaseModel, ConfigDict` |
| **Déclaration** | `class Config:` | `model_config = ConfigDict(...)` |
| **Position** | Après les champs | **AVANT** les champs (recommandé) |
| **Docstring** | Avant `class Config` | Après `model_config` |

### 2. Options de Configuration Courantes

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        # Validation stricte des types
        strict=True,
        
        # Autoriser les champs supplémentaires
        extra='allow',  # 'allow' | 'forbid' | 'ignore'
        
        # Exemples pour la documentation
        json_schema_extra={
            "example": {...}
        },
        
        # Valider les assignations
        validate_assignment=True,
        
        # Utiliser les alias pour la sérialisation
        populate_by_name=True,
        
        # ORM mode (SQLAlchemy)
        from_attributes=True,
        
        # Schéma JSON personnalisé
        json_schema_mode='validation',  # 'validation' | 'serialization'
        
        # Encoders personnalisés
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    # Champs du modèle ici...
```

### 3. Migration orm_mode → from_attributes

```python
# ❌ Pydantic v1
class UserRead(BaseModel):
    class Config:
        orm_mode = True

# ✅ Pydantic v2
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

### 4. Migration allow_population_by_field_name → populate_by_name

```python
# ❌ Pydantic v1
class UserUpdate(BaseModel):
    class Config:
        allow_population_by_field_name = True

# ✅ Pydantic v2
class UserUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
```

---

## 🔧 Exemples Complets pour B-CraftD v3.0

### Exemple 1 : Schéma Base (Lecture)

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ResourceBase(BaseModel):
    """Schéma de base pour une ressource"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID de la ressource")
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la ressource")
    description: Optional[str] = Field(None, description="Description")
    base_value: float = Field(..., ge=0, description="Valeur de base")
    stack_size: int = Field(..., ge=1, le=999, description="Taille du stack")
    is_tradeable: bool = Field(default=True, description="Échangeable sur le marché")
    is_craftable: bool = Field(default=False, description="Peut être crafté")
```

### Exemple 2 : Schéma Création avec Exemples

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict

class RecipeCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Épée en Fer",
                    "resource_id": 15,
                    "profession_id": 2,
                    "required_level": 10,
                    "base_experience": 50,
                    "crafting_time": 120,
                    "output_quantity": 1,
                    "success_rate": 95.0,
                    "ingredients": [
                        {"resource_id": 1, "quantity": 5},
                        {"resource_id": 3, "quantity": 2}
                    ]
                }
            ]
        }
    )
    
    """Schéma pour créer une nouvelle recette"""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la recette")
    resource_id: int = Field(..., description="ID de la ressource produite")
    profession_id: int = Field(..., description="ID de la profession requise")
    required_level: int = Field(..., ge=1, le=100, description="Niveau requis")
    base_experience: int = Field(..., ge=0, description="XP gagnée")
    crafting_time: int = Field(..., ge=1, description="Temps de craft (secondes)")
    output_quantity: int = Field(default=1, ge=1, description="Quantité produite")
    success_rate: float = Field(default=100.0, ge=0, le=100, description="Taux de réussite (%)")
    workshop_id: Optional[int] = Field(None, description="ID de l'atelier requis")
    ingredients: List[Dict[str, int]] = Field(..., description="Liste des ingrédients")
```

### Exemple 3 : Schéma Mise à Jour (Champs Optionnels)

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class UserUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "email": "new.email@example.com",
                    "role": "moderator"
                }
            ]
        }
    )
    
    """Schéma pour mettre à jour un utilisateur"""
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    role: Optional[str] = Field(None, pattern=r'^(player|moderator|admin)$')
    is_active: Optional[bool] = None
```

### Exemple 4 : Schéma avec Relations (SQLAlchemy)

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class ProfessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    type: str
    description: Optional[str]
    max_level: int
    unlock_level: int

class UserProgressionRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "user_id": 1,
                    "login": "player123",
                    "level": 25,
                    "coins": 1500.50,
                    "professions": [
                        {"id": 1, "name": "Mineur", "level": 30},
                        {"id": 2, "name": "Forgeron", "level": 20}
                    ]
                }
            ]
        }
    )
    
    """Schéma de lecture pour la progression complète d'un utilisateur"""
    user_id: int = Field(..., description="ID de l'utilisateur")
    login: str = Field(..., description="Nom d'utilisateur")
    level: int = Field(..., description="Niveau du personnage")
    experience: int = Field(..., description="XP du personnage")
    coins: float = Field(..., description="Monnaie")
    professions: List[ProfessionRead] = Field(default=[], description="Liste des professions")
    created_at: datetime = Field(..., description="Date de création")
```

### Exemple 5 : Schéma avec Validation Personnalisée

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Dict

class MarketListingCreate(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "resource_id": 10,
                    "quantity": 50,
                    "unit_price": 125.50,
                    "duration_hours": 48
                }
            ]
        }
    )
    
    """Schéma pour créer une offre sur le marché"""
    resource_id: int = Field(..., gt=0, description="ID de la ressource")
    quantity: int = Field(..., gt=0, description="Quantité à vendre")
    unit_price: float = Field(..., gt=0, description="Prix unitaire")
    duration_hours: int = Field(default=24, ge=1, le=168, description="Durée de l'offre (heures)")
    
    @field_validator('unit_price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Valider que le prix est raisonnable"""
        if v > 1_000_000:
            raise ValueError("Prix unitaire trop élevé (max: 1,000,000)")
        return round(v, 2)
    
    @model_validator(mode='after')
    def validate_total_price(self) -> 'MarketListingCreate':
        """Valider le prix total"""
        total = self.quantity * self.unit_price
        if total > 10_000_000:
            raise ValueError("Prix total trop élevé (max: 10,000,000)")
        return self
```

---

## 🔄 Guide de Migration Rapide

### Étape 1 : Identifier les Anciens Schémas

```bash
# Chercher tous les schémas avec class Config
grep -r "class Config:" schemas/
```

### Étape 2 : Ajouter l'Import ConfigDict

```python
# En haut de chaque fichier schemas/*.py
from pydantic import BaseModel, Field, ConfigDict
```

### Étape 3 : Convertir Chaque Schéma

```python
# AVANT
class MySchema(BaseModel):
    field: str
    
    class Config:
        orm_mode = True
        json_schema_extra = {"example": {...}}

# APRÈS
class MySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # orm_mode → from_attributes
        json_schema_extra={"example": {...}}
    )
    
    field: str
```

### Étape 4 : Tester

```bash
python -m pytest tests/test_schemas.py -v
```

---

## 📦 Structure des Dossiers Schémas

```
schemas/
├── __init__.py
├── user.py          # UserCreate, UserUpdate, UserRead, UserLogin
├── profession.py    # ProfessionCreate, ProfessionRead, UserProfessionRead
├── resource.py      # ResourceCreate, ResourceRead, ResourceUpdate
├── recipe.py        # RecipeCreate, RecipeRead, RecipeUpdate
├── inventory.py     # InventoryRead, InventoryUpdate
├── market.py        # MarketListingCreate, MarketListingRead, MarketPurchase
├── workshop.py      # WorkshopCreate, WorkshopRead, WorkshopUse
├── environment.py   # WeatherRead, SeasonRead, BiomeRead
├── craft.py         # CraftRequest, CraftResult
└── common.py        # Schémas réutilisables (Pagination, Response, Error)
```

---

## ⚠️ Pièges Courants à Éviter

### 1. Oublier l'Import ConfigDict

```python
# ❌ ERREUR
from pydantic import BaseModel

class MySchema(BaseModel):
    model_config = ConfigDict(...)  # NameError: ConfigDict not defined

# ✅ CORRECT
from pydantic import BaseModel, ConfigDict

class MySchema(BaseModel):
    model_config = ConfigDict(...)
```

### 2. Utiliser class Config en v2

```python
# ❌ ERREUR (déprécié, fonctionne mais warning)
class MySchema(BaseModel):
    class Config:
        orm_mode = True

# ✅ CORRECT
class MySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

### 3. Mauvais Placement du model_config

```python
# ❌ ERREUR (après les champs)
class MySchema(BaseModel):
    field: str
    model_config = ConfigDict(...)  # Peut causer des problèmes

# ✅ CORRECT (avant les champs)
class MySchema(BaseModel):
    model_config = ConfigDict(...)
    field: str
```

### 4. Oublier de Migrer les Options

```python
# ❌ ERREUR
model_config = ConfigDict(orm_mode=True)  # Ancien nom

# ✅ CORRECT
model_config = ConfigDict(from_attributes=True)  # Nouveau nom
```

---

## 🧪 Tests de Validation

```python
import pytest
from pydantic import ValidationError
from schemas.recipe import RecipeCreate

def test_recipe_create_valid():
    """Test création recette valide"""
    data = {
        "name": "Épée en Fer",
        "resource_id": 15,
        "profession_id": 2,
        "required_level": 10,
        "base_experience": 50,
        "crafting_time": 120,
        "ingredients": [{"resource_id": 1, "quantity": 5}]
    }
    recipe = RecipeCreate(**data)
    assert recipe.name == "Épée en Fer"
    assert recipe.output_quantity == 1  # Valeur par défaut

def test_recipe_create_invalid_level():
    """Test niveau requis invalide"""
    data = {
        "name": "Test",
        "resource_id": 1,
        "profession_id": 1,
        "required_level": 150,  # > 100
        "base_experience": 10,
        "crafting_time": 60,
        "ingredients": []
    }
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreate(**data)
    
    assert "required_level" in str(exc_info.value)

def test_recipe_model_config():
    """Test que model_config est bien configuré"""
    assert hasattr(RecipeCreate, 'model_config')
    assert 'json_schema_extra' in RecipeCreate.model_config
```

---

## 📚 Ressources Officielles

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [ConfigDict Documentation](https://docs.pydantic.dev/2.8/concepts/config/)
- [Model Config Options](https://docs.pydantic.dev/latest/api/config/)
- [Breaking Changes v1 → v2](https://docs.pydantic.dev/latest/migration/#breaking-changes)

---

## ✅ Checklist de Migration

- [ ] Installer Pydantic v2.12.5 : `pip install pydantic==2.12.5`
- [ ] Ajouter import ConfigDict dans tous les fichiers schemas/
- [ ] Convertir `class Config:` en `model_config = ConfigDict(...)`
- [ ] Remplacer `orm_mode` par `from_attributes`
- [ ] Remplacer `allow_population_by_field_name` par `populate_by_name`
- [ ] Placer `model_config` avant les champs
- [ ] Placer docstring après `model_config`
- [ ] Tester tous les schémas : `pytest tests/test_schemas.py`
- [ ] Vérifier OpenAPI : `/docs` (Swagger UI)
- [ ] Valider exemples JSON dans la documentation

---

## 🎯 Résumé : Règle Unique à Retenir

```python
# Template universel Pydantic v2.12.5 pour B-CraftD v3.0
from pydantic import BaseModel, Field, ConfigDict

class MySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,           # Pour SQLAlchemy
        populate_by_name=True,           # Pour alias
        validate_assignment=True,        # Validation stricte
        json_schema_extra={
            "examples": [{"key": "value"}]
        }
    )
    
    """Documentation du schéma ici"""
    field: type = Field(..., description="Description")
```

---

**Dernière mise à jour** : 4 décembre 2025  
**Version Pydantic** : 2.12.5  
**Statut** : ✅ Guide de référence officiel B-CraftD v3.0