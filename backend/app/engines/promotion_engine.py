from __future__ import annotations
import json, os, time, random
from typing import Dict, Any

SWARM_PATH = "backend/data/swarm_leaderboard.json"
VAR_TRACK_PATH = "backend/data/variant_tracking.json"
POST_LOG_PATH = "backend/data/promotion_log.json"

PLATFORMS = ["twitter", "reddit", "shorts"]

def _load(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _find_link(product: str, headline: str):
    store = _load(VAR_TRACK_PATH)
    key = f"{product}||{headline}"
    return store.get(key, {}).get("url")

def generate_post(headline: str, link: str) -> str:
    styles = [
        f"{headline}\n\nStart here → {link}",
        f"{headline}.\n\nTry it now: {link}",
        f"People are sleeping on this:\n{headline}\n\n{link}",
        f"{headline}\n\nThis changes everything → {link}"
    ]
    return random.choice(styles)

def run_promotion() -> Dict[str, Any]:
    swarm = _load(SWARM_PATH)
    log = _load(POST_LOG_PATH)

    if not swarm:
        return {"status": "no_swarm_data"}

    top = swarm[0]
    product = top.get("product")
    headline = top.get("headline")

    link = _find_link(product, headline)

    if not link:
        return {"status": "no_link_found"}

    post = generate_post(headline, link)
    platform = random.choice(PLATFORMS)

    entry = {
        "product": product,
        "headline": headline,
        "post": post,
        "platform": platform,
        "timestamp": time.time()
    }

    log.append(entry)
    _save(POST_LOG_PATH, log)

    return {
        "status": "posted",
        "platform": platform,
        "post": post,
        "headline": headline
    }
