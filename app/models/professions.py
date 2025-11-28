from dataclasses import dataclass, field
from typing import List

@dataclass
class Profession:
    id: str
    name: str
    description: str = ""
    resources_found: List[str] = field(default_factory=list)
    allowed_recipes: List[str] = field(default_factory=list)
    subclasses: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resources_found": self.resources_found,
            "allowed_recipes": self.allowed_recipes,
            "subclasses": self.subclasses
        }