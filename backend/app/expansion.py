import os
import json
import random
from datetime import datetime

DATA_DIR = "backend/data"
STORE_FILE = os.path.join(DATA_DIR, "store.json")
ANALYTICS_FILE = os.path.join(DATA_DIR, "analytics.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_content_assets(product):
    title = product.get("title")

    hooks = [
        f"This {title} is blowing up right now",
        f"Nobody is talking about this method...",
        f"This changes everything for beginners"
    ]

    return {
        "title": title,
        "tiktok_hooks": hooks,
        "youtube_title": f"{title} (Full Guide)",
        "script": f"Today we’re breaking down: {title}..."
    }

def update_analytics(products):
    data = load_json(ANALYTICS_FILE, {"history": []})

    for p in products:
        data["history"].append({
            "title": p.get("title"),
            "timestamp": datetime.utcnow().isoformat()
        })

    save_json(ANALYTICS_FILE, data)

def run_expansion():
    store = load_json(STORE_FILE, [])

    outputs = []
    for product in store:
        content = generate_content_assets(product)
        outputs.append(content)

    update_analytics(store)

    return {
        "generated_assets": outputs,
        "count": len(outputs)
    }
