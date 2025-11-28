from dataclasses import dataclass
from typing import Dict
from .resources import Resource

@dataclass
class Recipe:
    output: str
    ingredients: Dict[str, int]
    required_profession: str

    def to_dict(self) -> Dict:
        return {
            "output": self.output,
            "ingredients": self.ingredients,
            "required_profession": self.required_profession
        }