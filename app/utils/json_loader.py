import json
from pathlib import Path

def load_json(path: str):
    p = Path(path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)
    return data

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }
