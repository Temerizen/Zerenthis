from __future__ import annotations
import json, os, time, uuid
from typing import Dict, Any

TRACK_PATH = "backend/data/tracking_links.json"
CONVERSION_PATH = "backend/data/conversion_memory.json"

def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_tracking_link(product: str) -> Dict[str, Any]:
    data = _load(TRACK_PATH)
    if product in data:
        return data[product]

    link_id = str(uuid.uuid4())[:8]

    record = {
        "product": product,
        "link_id": link_id,
        "url": f"http://127.0.0.1:8000/api/track/{link_id}",
        "created_at": time.time()
    }

    data[product] = record
    _save(TRACK_PATH, data)
    return record

def log_conversion(link_id: str) -> Dict[str, Any]:
    links = _load(TRACK_PATH)
    conversions = _load(CONVERSION_PATH)

    if not isinstance(conversions, dict):
        conversions = {}

    product = None
    for k, v in links.items():
        if v.get("link_id") == link_id:
            product = k
            break

    if not product:
        return {"status": "error", "reason": "invalid_link"}

    if product not in conversions:
        conversions[product] = {
            "clicks": 0,
            "last_click": None
        }

    conversions[product]["clicks"] += 1
    conversions[product]["last_click"] = time.time()

    _save(CONVERSION_PATH, conversions)

    return {
        "status": "ok",
        "product": product,
        "clicks": conversions[product]["clicks"]
    }
