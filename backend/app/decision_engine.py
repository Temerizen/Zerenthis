import os
import json
from datetime import datetime

DATA_DIR = "backend/data"
PACKS_FILE = os.path.join(DATA_DIR, "packs.json")
DECISIONS_FILE = os.path.join(DATA_DIR, "decisions.json")

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

def build_queue():
    packs = load_json(PACKS_FILE, [])
    queue = []

    for p in packs:
        p["score"] = score_pack(p)
        p["status"] = p.get("status", "pending")
        queue.append(p)

    queue = sorted(queue, key=lambda x: x["score"], reverse=True)

    save_json(DECISIONS_FILE, queue)
    return queue

def get_ranked():
    return load_json(DECISIONS_FILE, [])

def get_next():
    queue = load_json(DECISIONS_FILE, [])

    for item in queue:
        if item.get("status") != "posted":
            return item

    return {"message": "No content available"}

def mark_posted(title):
    queue = load_json(DECISIONS_FILE, [])

    for item in queue:
        if item.get("topic") == title:
            item["status"] = "posted"
            item["posted_at"] = datetime.utcnow().isoformat()

    save_json(DECISIONS_FILE, queue)
    return {"status": "updated"}
