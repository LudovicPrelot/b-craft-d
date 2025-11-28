# scripts/create_admin.py
import uuid, json, getpass
import config
from utils.auth import hash_password

def main():
    users = {}
    try:
        users = json.loads(config.USERS_FILE.read_text(encoding='utf-8'))
    except Exception:
        users = {}
    login = input("Login admin: ")
    firstname = input("Prénom: ")
    lastname = input("Nom: ")
    mail = input("Mail: ")
    pw = getpass.getpass("Password: ")
    uid = str(uuid.uuid4())
    users[uid] = {
        "id": uid,
        "firstname": firstname,
        "lastname": lastname,
        "mail": mail,
        "login": login,
        "password_hash": hash_password(pw),
        "profession": "",
        "subclasses": [],
        "is_admin": True,
        "is_moderator": True
    }
    config.USERS_FILE.write_text(json.dumps(users, indent=4, ensure_ascii=False), encoding='utf-8')
    print("Admin créé:", uid)

if __name__=="__main__":
    main()
