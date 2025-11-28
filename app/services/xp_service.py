# services/xp_service.py

from typing import Dict, Tuple
from models.user import User

# formule simple d'XP pour niveau : next_level_xp = base * level^exponent
BASE_XP = 100
EXPONENT = 1.5

def xp_for_level(level: int) -> int:
    # XP required to reach `level` from level-1
    return int(BASE_XP * (level ** EXPONENT))

def total_xp_for_next_level(user: User) -> int:
    return xp_for_level(user.level)

def add_xp(user: User, amount: int) -> Tuple[int, int]:
    """
    Ajoute de l'xp à l'utilisateur, met à jour level si nécessaire.
    Retourne (new_xp, new_level)
    """
    if amount <= 0:
        return user.xp, user.level

    user.xp += amount
    leveled = False
    # loop in case of multiple levels gained
    while user.xp >= xp_for_level(user.level):
        user.xp -= xp_for_level(user.level)
        user.level += 1
        leveled = True
        # apply simple stat reward on level up
        _apply_level_rewards(user)

    return user.xp, user.level

def _apply_level_rewards(user: User):
    """
    Simple reward: increase stats slightly on level up.
    Could be replaced by complex rules later.
    """
    # give +1 stat to the lowest stat
    min_stat = min(user.stats, key=lambda k: user.stats[k])
    user.stats[min_stat] += 1
