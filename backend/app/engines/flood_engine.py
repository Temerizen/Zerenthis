from __future__ import annotations
import json, os, time, random
from typing import Dict, Any, List

SWARM_PATH = "backend/data/swarm_leaderboard.json"
VAR_TRACK_PATH = "backend/data/variant_tracking.json"
FLOOD_LOG_PATH = "backend/data/flood_log.json"

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

def _find_link(product, headline):
    store = _load(VAR_TRACK_PATH)
    key = f"{product}||{headline}"
    return store.get(key, {}).get("url")

def _generate_post(headline, link):
    styles = [
        f"{headline}\n\nStart here → {link}",
        f"{headline}\n\nTry it now: {link}",
        f"People are sleeping on this:\n{headline}\n\n{link}",
        f"{headline}\n\nThis changes everything → {link}",
        f"Nobody talks about this:\n{headline}\n\n{link}"
    ]
    return random.choice(styles)

def run_flood(posts_per_run: int = 5) -> Dict[str, Any]:
    swarm = _load(SWARM_PATH)
    log = _load(FLOOD_LOG_PATH)

    if not swarm:
        return {"status": "no_swarm_data"}

    outputs = []

    top_variants = swarm[:3]  # use top 3 performers

    for i in range(posts_per_run):
        variant = random.choice(top_variants)

        product = variant.get("product")
        headline = variant.get("headline")
        link = _find_link(product, headline)

        if not link:
            continue

        post = _generate_post(headline, link)
        platform = random.choice(PLATFORMS)

        entry = {
            "product": product,
            "headline": headline,
            "post": post,
            "platform": platform,
            "timestamp": time.time()
        }

        outputs.append(entry)
        log.append(entry)

    _save(FLOOD_LOG_PATH, log)

    return {
        "status": "flood_generated",
        "count": len(outputs),
        "posts": outputs
    }
