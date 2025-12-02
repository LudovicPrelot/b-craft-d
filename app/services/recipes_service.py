from typing import Dict, List, Optional
from pathlib import Path
import json
from app.models.recipe import Recipe
import config

class RecipeService:
    @staticmethod
    def _load() -> Dict[str, dict]:
        if not config.RECIPES_FILE.exists():
            return {}
        try:
            return json.loads(config.RECIPES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @staticmethod
    def _save(data: Dict[str, dict]):
        config.RECIPES_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def list(cls) -> List[Recipe]:
        raw = cls._load()
        return [Recipe(**item) for item in raw.values()]

    @classmethod
    def get(cls, recipe_id: str) -> Optional[Recipe]:
        raw = cls._load()
        if recipe_id not in raw:
            return None
        return Recipe(**raw[recipe_id])

    @classmethod
    def create(cls, recipe: Recipe):
        raw = cls._load()
        if recipe.id in raw:
            raise ValueError("Recipe ID already exists")
        raw[recipe.id] = recipe.__dict__
        cls._save(raw)
        return recipe

    @classmethod
    def update(cls, recipe_id: str, data: dict) -> Recipe:
        raw = cls._load()
        if recipe_id not in raw:
            raise ValueError("Recipe not found")
        raw[recipe_id].update(data)
        cls._save(raw)
        return Recipe(**raw[recipe_id])

    @classmethod
    def delete(cls, recipe_id: str) -> bool:
        raw = cls._load()
        if recipe_id not in raw:
            return False
        del raw[recipe_id]
        cls._save(raw)
        return True
