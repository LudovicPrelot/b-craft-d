from dataclasses import dataclass

@dataclass
class Resource:
    id: str
    name: str
    type: str
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
        }
