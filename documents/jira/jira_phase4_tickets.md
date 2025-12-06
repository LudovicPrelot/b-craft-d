# 🎫 JIRA Tickets - Phase 4 : Modèles SQLAlchemy

**Date** : 4 décembre 2025  
**Phase** : 4 - Modèles SQLAlchemy  
**Durée estimée** : 3 jours  

---

## 📋 Nomenclature des Tickets

**Format** : `{type}_{version}_{phase}_{numéro}`

**Types** :
- `FEAT` - Feature (nouvelle fonctionnalité)
- `REFACTOR` - Refactoring (modification modèle existant)
- `TEST` - Tests unitaires
- `DOC` - Documentation

**Exemple** : `FEAT_V3_P4_001` - Feature v3.0, Phase 4, Ticket 001

---

## 🎯 Epic : Phase 4 - Modèles SQLAlchemy

**Epic ID** : `EPIC_V3_P4`  
**Objectif** : Créer tous les modèles SQLAlchemy pour B-CraftD v3.0  
**Story Points** : 21  

---

## 📦 Sprint 1 : Modèles Environnement (4 tickets)

### FEAT_V3_P4_001 : Créer modèle Weather
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Créer le modèle SQLAlchemy pour la table `weathers`

**Critères d'acceptation** :
- [ ] Classe `Weather` hérite de `Base`
- [ ] Tous les champs de la table `weathers` mappés
- [ ] Relations définies (resources_weathers)
- [ ] Méthode `to_dict()` implémentée
- [ ] Validations Pydantic v2 (ConfigDict)
- [ ] Docstring complète

**Fichier** : `models/weather.py`

---

### FEAT_V3_P4_002 : Créer modèle Season
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Créer le modèle SQLAlchemy pour la table `seasons`

**Critères d'acceptation** :
- [ ] Classe `Season` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies
- [ ] Méthode `get_current_season()` statique
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/season.py`

---

### FEAT_V3_P4_003 : Créer modèle Biome
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Créer le modèle SQLAlchemy pour la table `biomes`

**Critères d'acceptation** :
- [ ] Classe `Biome` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (resources_biomes, workshops_biomes)
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/biome.py`

---

### FEAT_V3_P4_004 : Créer modèle Rarity
**Priorité** : Haute  
**Story Points** : 1  
**Description** : Créer le modèle SQLAlchemy pour la table `rarities`

**Critères d'acceptation** :
- [ ] Classe `Rarity` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (resources)
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/rarity.py`

---

## 📦 Sprint 2 : Modèles Professions (4 tickets)

### FEAT_V3_P4_005 : Créer modèle Subclass
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Créer le modèle SQLAlchemy pour la table `subclasses`

**Critères d'acceptation** :
- [ ] Classe `Subclass` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (profession, users_subclasses)
- [ ] Propriété calculée `is_unlockable_by(user)`
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/subclass.py`

---

### FEAT_V3_P4_006 : Créer modèle MasteryRank
**Priorité** : Haute  
**Story Points** : 1  
**Description** : Créer le modèle SQLAlchemy pour la table `mastery_rank`

**Critères d'acceptation** :
- [ ] Classe `MasteryRank` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (users_professions)
- [ ] Méthode statique `get_rank_for_level(level)`
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/mastery_rank.py`

---

### REFACTOR_V3_P4_007 : Adapter modèle UserProfession
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Adapter le modèle existant pour v3.0 (ajout mastery_rank_id)

**Critères d'acceptation** :
- [ ] Champ `mastery_rank_id` ajouté
- [ ] Relation `mastery_rank` définie
- [ ] Propriété calculée `next_level_xp`
- [ ] Propriété calculée `progress_percent`
- [ ] Méthode `can_level_up()`
- [ ] Méthode `to_dict()` mise à jour

**Fichier** : `models/user_profession.py`

---

### FEAT_V3_P4_008 : Créer modèle UserSubclass
**Priorité** : Moyenne  
**Story Points** : 1  
**Description** : Créer le modèle pour la table `users_subclasses`

**Critères d'acceptation** :
- [ ] Classe `UserSubclass` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (user, subclass)
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/user_subclass.py`

---

## 📦 Sprint 3 : Modèles Workshops (3 tickets)

### FEAT_V3_P4_009 : Créer modèle Workshop
**Priorité** : Haute  
**Story Points** : 3  
**Description** : Créer le modèle SQLAlchemy pour la table `workshops`

**Critères d'acceptation** :
- [ ] Classe `Workshop` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (profession, resources, biomes)
- [ ] Propriété calculée `is_broken` (durability == 0)
- [ ] Propriété calculée `durability_percent`
- [ ] Méthode `use(amount=5)` pour usure
- [ ] Méthode `repair()` pour réparation
- [ ] Méthode `calculate_repair_cost()`
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/workshop.py`

---

### FEAT_V3_P4_010 : Créer modèle WorkshopResource
**Priorité** : Moyenne  
**Story Points** : 1  
**Description** : Créer le modèle pour la table `workshops_resources`

**Critères d'acceptation** :
- [ ] Classe `WorkshopResource` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (workshop, resource)
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/workshop_resource.py`

---

### FEAT_V3_P4_011 : Créer modèle WorkshopBiome
**Priorité** : Moyenne  
**Story Points** : 1  
**Description** : Créer le modèle pour la table `workshops_biomes`

**Critères d'acceptation** :
- [ ] Classe `WorkshopBiome` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (workshop, biome)
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/workshop_biome.py`

---

## 📦 Sprint 4 : Modèles Marché (2 tickets)

### FEAT_V3_P4_012 : Créer modèle MarketStatus
**Priorité** : Haute  
**Story Points** : 1  
**Description** : Créer le modèle pour la table `market_status`

**Critères d'acceptation** :
- [ ] Classe `MarketStatus` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (markets)
- [ ] Constantes de classe (ACTIVE, SOLD, CANCELLED, EXPIRED, RESERVED)
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/market_status.py`

---

### FEAT_V3_P4_013 : Créer modèle Market
**Priorité** : Haute  
**Story Points** : 3  
**Description** : Créer le modèle SQLAlchemy pour la table `markets` (partitionnée)

**Critères d'acceptation** :
- [ ] Classe `Market` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relations définies (seller, buyer, resource, status)
- [ ] Propriété calculée `is_active`
- [ ] Propriété calculée `is_expired`
- [ ] Propriété calculée `time_remaining`
- [ ] Méthode `can_buy(user)` validation
- [ ] Méthode `complete_purchase(buyer)` transaction
- [ ] Méthode `cancel()` annulation
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/market.py`

---

## 📦 Sprint 5 : Modèles Statistiques & Devices (2 tickets)

### FEAT_V3_P4_014 : Créer modèle UserStatistics
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Créer le modèle pour la table `user_statistics`

**Critères d'acceptation** :
- [ ] Classe `UserStatistics` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relation définie (user)
- [ ] Méthode `increment_craft()`
- [ ] Méthode `increment_sale(amount)`
- [ ] Méthode `increment_purchase(amount)`
- [ ] Méthode `increment_gather(amount)`
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/user_statistics.py`

---

### FEAT_V3_P4_015 : Créer modèle Device
**Priorité** : Basse  
**Story Points** : 1  
**Description** : Créer le modèle pour la table `devices`

**Critères d'acceptation** :
- [ ] Classe `Device` hérite de `Base`
- [ ] Tous les champs mappés
- [ ] Relation définie (user)
- [ ] Méthode `update_last_used()`
- [ ] Méthode `to_dict()`
- [ ] Docstring complète

**Fichier** : `models/device.py`

---

## 📦 Sprint 6 : Refactoring Modèles Existants (5 tickets)

### REFACTOR_V3_P4_016 : Adapter modèle User
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Adapter User pour v3.0 (multi-professions, statistics)

**Critères d'acceptation** :
- [ ] Relations `professions` (list) au lieu de `profession` (single)
- [ ] Relation `subclasses` ajoutée
- [ ] Relation `statistics` ajoutée
- [ ] Relation `devices` ajoutée
- [ ] Propriété calculée `active_professions_count`
- [ ] Propriété calculée `total_profession_levels`
- [ ] Méthode `can_add_profession()` (max 3)
- [ ] Méthode `to_dict()` mise à jour

**Fichier** : `models/user.py`

---

### REFACTOR_V3_P4_017 : Adapter modèle Profession
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Adapter Profession pour hiérarchie parent/enfant

**Critères d'acceptation** :
- [ ] Relation `parent` ajoutée
- [ ] Relation `children` ajoutée
- [ ] Relation `subclasses` ajoutée
- [ ] Propriété calculée `is_parent` (has children)
- [ ] Propriété calculée `is_child` (has parent)
- [ ] Méthode `get_full_tree()` récursive
- [ ] Méthode `to_dict()` mise à jour

**Fichier** : `models/profession.py`

---

### REFACTOR_V3_P4_018 : Adapter modèle Resource
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Adapter Resource pour environnement (biomes, weathers, seasons)

**Critères d'acceptation** :
- [ ] Relation `rarity` ajoutée
- [ ] Relation `type` ajoutée
- [ ] Relations `biomes`, `weathers`, `seasons` ajoutées via tables d'association
- [ ] Propriété calculée `adjusted_value` (base_value * rarity_multiplier)
- [ ] Méthode `get_spawn_chance(biome_id)`
- [ ] Méthode `get_weather_multiplier(weather_id)`
- [ ] Méthode `to_dict()` mise à jour avec relations

**Fichier** : `models/resource.py`

---

### REFACTOR_V3_P4_019 : Adapter modèle Recipe
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Adapter Recipe pour workshop_id optionnel

**Critères d'acceptation** :
- [ ] Champ `workshop_id` ajouté (nullable)
- [ ] Relation `workshop` ajoutée
- [ ] Propriété calculée `requires_workshop`
- [ ] Méthode `can_craft(user, inventory)` validation complète
- [ ] Méthode `get_missing_ingredients(inventory)`
- [ ] Méthode `calculate_craft_time(weather, season, mastery)`
- [ ] Méthode `to_dict()` mise à jour

**Fichier** : `models/recipe.py`

---

### REFACTOR_V3_P4_020 : Adapter modèle Inventory
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Adapter Inventory pour validation stack_size

**Critères d'acceptation** :
- [ ] Relation `resource` enrichie (eager loading)
- [ ] Propriété calculée `is_full` (quantity >= stack_size)
- [ ] Propriété calculée `remaining_space` (stack_size - quantity)
- [ ] Méthode `add(amount)` avec validation stack
- [ ] Méthode `remove(amount)` avec validation quantité
- [ ] Méthode `calculate_value()` (quantity * resource.adjusted_value)
- [ ] Méthode `to_dict()` mise à jour

**Fichier** : `models/inventory.py`

---

## 📦 Sprint 7 : Tests Unitaires (3 tickets)

### TEST_V3_P4_021 : Tests modèles Environnement
**Priorité** : Haute  
**Story Points** : 2  
**Description** : Tests unitaires Weather, Season, Biome, Rarity

**Critères d'acceptation** :
- [ ] Tests création/lecture/suppression
- [ ] Tests relations
- [ ] Tests méthodes calculées
- [ ] Tests validations Pydantic
- [ ] Coverage >90%

**Fichier** : `tests/test_models_environment.py`

---

### TEST_V3_P4_022 : Tests modèles Professions & Workshops
**Priorité** : Haute  
**Story Points** : 3  
**Description** : Tests Subclass, MasteryRank, Workshop, UserProfession

**Critères d'acceptation** :
- [ ] Tests hiérarchie professions
- [ ] Tests workshop usure/réparation
- [ ] Tests mastery rank promotion
- [ ] Tests validations métier
- [ ] Coverage >90%

**Fichier** : `tests/test_models_professions.py`

---

### TEST_V3_P4_023 : Tests modèles Marché & Stats
**Priorité** : Haute  
**Story Points** : 3  
**Description** : Tests Market, UserStatistics, modèles refactorés

**Critères d'acceptation** :
- [ ] Tests transactions marché complètes
- [ ] Tests expiration offres
- [ ] Tests statistiques incrémentation
- [ ] Tests modèles User/Resource/Recipe adaptés
- [ ] Coverage >90%

**Fichier** : `tests/test_models_market.py`

---

## 📦 Sprint 8 : Documentation (1 ticket)

### DOC_V3_P4_024 : Documentation modèles SQLAlchemy
**Priorité** : Moyenne  
**Story Points** : 2  
**Description** : Créer documentation complète des modèles

**Critères d'acceptation** :
- [ ] Diagramme ERD mis à jour (27 tables)
- [ ] Documentation chaque modèle (relations, propriétés)
- [ ] Exemples d'utilisation par modèle
- [ ] Guide migration modèles v2 → v3
- [ ] Fichier MODELS_V3.md complet

**Fichier** : `docs/MODELS_V3.md`

---

## 📊 Résumé Phase 4

**Total tickets** : 24  
**Story Points** : 48  
**Sprints** : 8  
**Durée estimée** : 3 jours (6h/jour = 18h)

### Répartition par type

| Type | Tickets | Story Points |
|------|---------|--------------|
| FEAT | 15 | 26 |
| REFACTOR | 6 | 14 |
| TEST | 3 | 8 |
| DOC | 1 | 2 |
| **TOTAL** | **24** | **48** |

### Ordre d'exécution

1. **Jour 1** : Sprints 1-3 (Environnement + Professions + Workshops) - 15 tickets
2. **Jour 2** : Sprints 4-6 (Marché + Stats + Refactoring) - 9 tickets  
3. **Jour 3** : Sprints 7-8 (Tests + Documentation) - 4 tickets

---

## 🎯 Règles de Développement

### Conventions Pydantic v2.12.5

**OBLIGATOIRE pour tous les modèles** :

```python
from pydantic import ConfigDict

class MyModel(Base):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
```

### Structure fichier modèle type

```python
"""
Module: models.my_model
Description: Modèle SQLAlchemy pour la table my_table
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import ConfigDict
from database import Base


class MyModel(Base):
    """Modèle pour la table my_table"""
    
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    __tablename__ = "my_table"
    
    # Colonnes
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    # Relations
    items = relationship("Item", back_populates="my_model")
    
    # Propriétés calculées
    @property
    def display_name(self) -> str:
        """Nom formaté pour affichage"""
        return self.name.upper()
    
    # Méthodes métier
    def can_do_action(self) -> bool:
        """Vérifie si l'action est possible"""
        return True
    
    # Sérialisation
    def to_dict(self) -> dict:
        """Convertit en dictionnaire"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name
        }
```

---

**Date de création** : 4 décembre 2025  
**Dernière mise à jour** : 4 décembre 2025