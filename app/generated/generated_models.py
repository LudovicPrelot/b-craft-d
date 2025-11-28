from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Resource:
    id: str
    name: str
    type: str
    description: str

@dataclass
class Recipe:
    output: str
    ingredients: Dict[str, Any]
    required_profession: str

@dataclass
class Profession:
    id: str
    name: str
    resources_found: List[str]
    allowed_recipes: List[str]
    subclasses: List[str]
