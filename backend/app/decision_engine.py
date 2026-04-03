import os
import json
from datetime import datetime
from .packs_store import get_packs

DATA_DIR = "backend/data"
DECISIONS_FILE = os.path.join(DATA_DIR, "decisions.json")

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

def score_pack(pack):
    score = 0
    topic = (pack.get("topic") or "").lower()
    content = pack.get("content") or ""
    buyer = (pack.get("buyer") or "").lower()
    niche = (pack.get("niche") or "").lower()

    if any(x in topic for x in ["tiktok", "youtube", "shorts", "ai", "money", "automation", "viral"]):
        score += 3
    if any(x in niche for x in ["content", "entertainment", "monetization"]):
        score += 2
    if len(content) > 500:
        score += 2
    if "beginner" in buyer or "new creator" in buyer or "new creators" in buyer:
        score += 1
    return score

def build_queue():
    packs = get_packs()
    queue = []
    for p in packs:
        item = dict(p)
        item["score"] = score_pack(item)
        item["status"] = item.get("status", "pending")
        queue.append(item)
    queue = sorted(queue, key=lambda x: x.get("score", 0), reverse=True)
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
    return {"status": "updated", "title": title}
