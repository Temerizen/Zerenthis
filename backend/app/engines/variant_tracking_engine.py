from __future__ import annotations
import json, os, time, uuid
from typing import Dict, Any

VAR_TRACK_PATH = "backend/data/variant_tracking.json"
VAR_CONV_PATH = "backend/data/variant_conversions.json"

def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_variant_link(product: str, headline: str) -> Dict[str, Any]:
    store = _load(VAR_TRACK_PATH)
    key = f"{product}||{headline}"

    if key in store:
        return store[key]

    vid = str(uuid.uuid4())[:8]
    rec = {
        "product": product,
        "headline": headline,
        "variant_id": vid,
        "url": f"http://127.0.0.1:8000/api/track/variant/{vid}",
        "created_at": time.time()
    }
    store[key] = rec
    _save(VAR_TRACK_PATH, store)
    return rec

def log_variant_click(variant_id: str) -> Dict[str, Any]:
    store = _load(VAR_TRACK_PATH)
    conv = _load(VAR_CONV_PATH)

    # find record
    rec = None
    for _, v in store.items():
        if v.get("variant_id") == variant_id:
            rec = v
            break

    if not rec:
        return {"status": "error", "reason": "invalid_variant"}

    key = f"{rec['product']}||{rec['headline']}"
    if key not in conv:
        conv[key] = {
            "product": rec["product"],
            "headline": rec["headline"],
            "clicks": 0,
            "last_click": None
        }

    conv[key]["clicks"] += 1
    conv[key]["last_click"] = time.time()

    _save(VAR_CONV_PATH, conv)

    return {
        "status": "ok",
        "product": rec["product"],
        "headline": rec["headline"],
        "clicks": conv[key]["clicks"]
    }
