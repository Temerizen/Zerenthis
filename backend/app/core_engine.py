import os
import json
import random
from datetime import datetime

DATA_DIR = "backend/data"
PACKS_FILE = os.path.join(DATA_DIR, "packs.json")
WINNERS_FILE = os.path.join(DATA_DIR, "winners.json")
STORE_FILE = os.path.join(DATA_DIR, "store.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def score_pack(pack):
    score = 0
    topic = pack.get("topic", "").lower()

    if any(x in topic for x in ["tiktok", "ai", "money", "automation"]):
        score += 3

    if len(pack.get("content", "")) > 1500:
        score += 2

    if "beginner" in pack.get("buyer", "").lower():
        score += 1

    return score

def find_winners():
    packs = load_json(PACKS_FILE, [])
    winners = []

    for p in packs:
        s = score_pack(p)
        if s >= 4:
            p["score"] = s
            winners.append(p)

    save_json(WINNERS_FILE, winners)
    return winners

def create_listing(pack):
    return {
        "title": pack.get("topic"),
        "price": 19,
        "description": f"{pack.get('topic')}\n\nFor: {pack.get('buyer')}\n\n{pack.get('promise')}",
        "file": pack.get("file_name"),
        "created_at": datetime.utcnow().isoformat()
    }

def generate_store():
    winners = find_winners()
    listings = [create_listing(w) for w in winners]
    save_json(STORE_FILE, listings)
    return listings

