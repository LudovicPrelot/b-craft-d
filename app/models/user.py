# models/user.py
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class User:
    id: str
    firstname: str
    lastname: str
    mail: str
    login: str
    password_hash: str
    profession: str
    subclasses: List[str] = field(default_factory=list)
    inventory: Dict[str, int] = field(default_factory=dict)
    xp: int = 0                       # total XP
    level: int = 1                    # current level
    stats: Dict[str, int] = field(default_factory=lambda: {"strength": 1, "agility": 1, "endurance": 1})
    biome: str = ""                   # optional: user's preferred/current biome
    is_admin: bool = False
    is_moderator: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "mail": self.mail,
            "login": self.login,
            "password_hash": self.password_hash,
            "profession": self.profession,
            "subclasses": self.subclasses,
            "inventory": self.inventory,
            "xp": self.xp,
            "level": self.level,
            "stats": self.stats,
            "biome": self.biome,
            "is_admin": self.is_admin,
            "is_moderator": self.is_moderator
        }

    @classmethod
    def from_dict(cls, d: Dict):
        return cls(
            id=d["id"],
            firstname=d["firstname"],
            lastname=d["lastname"],
            mail=d["mail"],
            login=d["login"],
            password_hash=d["password_hash"],
            profession=d.get("profession",""),
            subclasses=d.get("subclasses", []),
            inventory=d.get("inventory", {}),
            xp=d.get("xp", 0),
            level=d.get("level", 1),
            stats=d.get("stats", {"strength":1,"agility":1,"endurance":1}),
            biome=d.get("biome", ""),
            is_admin=d.get("is_admin", False),
            is_moderator=d.get("is_moderator", False)
        )
