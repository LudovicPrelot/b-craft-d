# tests/test_admin.py

from models.user import User
from services.xp_service import add_xp
from utils.json import save_json, load_json
import uuid
import config

def test_admin_create_user():
    users = load_json(config.USERS_FILE)

    uid = str(uuid.uuid4())
    user = User(
        id=uid, firstname="Admin", lastname="Test",
        mail="admin@test.com", login="admintest",
        password_hash="x", profession="mineur"
    )

    users[uid] = user.to_dict()
    save_json(config.USERS_FILE, users)

    loaded = load_json(config.USERS_FILE)
    assert uid in loaded
    assert loaded[uid]["mail"] == "admin@test.com"

def test_admin_grant_xp():
    users = load_json(config.USERS_FILE)
    uid = list(users.keys())[0]
    user = User.from_dict(users[uid])

    before_level = user.level
    add_xp(user, 500)

    users[uid] = user.to_dict()
    save_json(config.USERS_FILE, users)

    updated = User.from_dict(load_json(config.USERS_FILE)[uid])
    assert updated.level >= before_level
