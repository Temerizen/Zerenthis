import os
import json
from datetime import datetime

DATA_DIR = "backend/data"
PACKS_FILE = os.path.join(DATA_DIR, "packs.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_packs():
    return load_json(PACKS_FILE, [])

def add_pack(topic, buyer="", promise="", content="", file_name="", niche="", tone="", bonus="", notes=""):
    packs = get_packs()
    pack = {
        "topic": topic,
        "buyer": buyer,
        "promise": promise,
        "content": content,
        "file_name": file_name,
        "niche": niche,
        "tone": tone,
        "bonus": bonus,
        "notes": notes,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    packs.append(pack)
    save_json(PACKS_FILE, packs)
    return pack

