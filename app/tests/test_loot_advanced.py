# tests/test_loot_advanced.py

from routes.loot_routes import weighted_choice, RARITY_MULTIPLIERS

def test_weighted_choice_distribution():
    """
    weighted_choice must respect weights statistically.
    """
    choices = [
        ({"item": "a"}, 10),
        ({"item": "b"}, 1)
    ]

    results = {"a": 0, "b": 0}

    for _ in range(1000):
        res = weighted_choice(choices)
        results[res["item"]] += 1

    assert results["a"] > results["b"]  # strongly weighted

def test_rarity_multipliers_exist():
    assert "common" in RARITY_MULTIPLIERS
    assert "legendary" in RARITY_MULTIPLIERS

    # legendary must be rarer than common
    assert RARITY_MULTIPLIERS["legendary"] < RARITY_MULTIPLIERS["common"]
