from typing import Dict, List, Optional
import json
from app.models.resource import Resource
import config

class ResourceService:
    @staticmethod
    def _load() -> Dict[str, dict]:
        if not config.RESOURCES_FILE.exists():
            return {}
        try:
            return json.loads(config.RESOURCES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @staticmethod
    def _save(data: Dict[str, dict]):
        config.RESOURCES_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def list(cls) -> List[Resource]:
        raw = cls._load()
        return [Resource(**item) for item in raw.values()]

    @classmethod
    def get(cls, resource_id: str) -> Optional[Resource]:
        raw = cls._load()
        if resource_id not in raw:
            return None
        return Resource(**raw[resource_id])

    @classmethod
    def create(cls, resource: Resource):
        raw = cls._load()
        if resource.id in raw:
            raise ValueError("Resource ID already exists")
        raw[resource.id] = resource.__dict__
        cls._save(raw)
        return resource

    @classmethod
    def update(cls, resource_id: str, data: dict) -> Resource:
        raw = cls._load()
        if resource_id not in raw:
            raise ValueError("Resource not found")
        raw[resource_id].update(data)
        cls._save(raw)
        return Resource(**raw[resource_id])

    @classmethod
    def delete(cls, resource_id: str) -> bool:
        raw = cls._load()
        if resource_id not in raw:
            return False
        del raw[resource_id]
        cls._save(raw)
        return True
