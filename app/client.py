import requests

BASE = "http://localhost:5000"

class CraftingClient:

    def __init__(self, token: str):
        self.headers = {"token": token}

    def get_resources(self, profession_id: str):
        r = requests.get(f"{BASE}/professions/{profession_id}/resources",
                         headers=self.headers)
        return r.json()

    def craft(self, profession_id: str, recipe_id: str, inventory: dict):
        r = requests.post(
            f"{BASE}/craft?profession_id={profession_id}&recipe_id={recipe_id}",
            headers=self.headers,
            json={"items": inventory}
        )
        return r.json()
