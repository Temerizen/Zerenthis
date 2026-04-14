import os, json
from typing import Dict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
CHAMP_FILE = os.path.join(BASE_DIR, "backend/data/champion.json")

def load_champion() -> Dict | None:
    if not os.path.exists(CHAMP_FILE):
        return None
    with open(CHAMP_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_champion(data: Dict):
    os.makedirs(os.path.dirname(CHAMP_FILE), exist_ok=True)
    with open(CHAMP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
