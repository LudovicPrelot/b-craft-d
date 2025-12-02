from typing import Dict, List, Optional
from pathlib import Path
import json
from app.models.profession import Profession
import config

class ProfessionService:
    @staticmethod
    def _load() -> Dict[str, dict]:
        path = config.PROFESSIONS_FILE
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @staticmethod
    def _save(data: Dict[str, dict]):
        path = config.PROFESSIONS_FILE
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def list(cls) -> List[Profession]:
        raw = cls._load()
        return [Profession(**item) for item in raw.values()]

    @classmethod
    def get(cls, profession_id: str) -> Optional[Profession]:
        raw = cls._load()
        if profession_id not in raw:
            return None
        return Profession(**raw[profession_id])

    @classmethod
    def create(cls, profession: Profession):
        raw = cls._load()
        if profession.id in raw:
            raise ValueError("Profession ID already exists")

        raw[profession.id] = profession.__dict__
        cls._save(raw)
        return profession

    @classmethod
    def update(cls, profession_id: str, data: dict) -> Profession:
        raw = cls._load()
        if profession_id not in raw:
            raise ValueError("Profession not found")

        raw[profession_id].update(data)
        cls._save(raw)
        return Profession(**raw[profession_id])

    @classmethod
    def delete(cls, profession_id: str) -> bool:
        raw = cls._load()
        if profession_id not in raw:
            return False
        del raw[profession_id]
        cls._save(raw)
        return True
