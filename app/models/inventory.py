from pydantic import BaseModel
from typing import Dict

class Inventory(BaseModel):
    items: Dict[str, int]

