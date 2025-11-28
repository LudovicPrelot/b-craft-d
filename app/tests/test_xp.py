# tests/test_xp.py

from services.xp_service import add_xp, xp_for_level
from models.user import User

def test_xp_gain_and_level_up():
    user = User(
        id="u1",
        firstname="A",
        lastname="B",
        mail="a@test.com",
        login="test",
        password_hash="x",
        profession="mineur"
    )

    # give XP slightly below level-up threshold
    threshold = xp_for_level(1)
    add_xp(user, threshold - 10)

    assert user.level == 1
    assert user.xp == threshold - 10

    # add remaining XP to level up
    add_xp(user, 10)
    assert user.level == 2
    assert user.xp == 0  # XP resets on level-up

def test_multi_level_up():
    user = User(
        id="u2", firstname="X", lastname="Y",
        mail="t@t.com", login="xy", password_hash="x",
        profession="mineur"
    )

    # give a large amount of XP to skip multiple levels
    add_xp(user, 2000)

    assert user.level > 2
    assert user.xp >= 0
