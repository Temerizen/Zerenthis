from __future__ import annotations
import json, os, time, random
from typing import Dict, Any, List

OPT_PATH = "backend/data/optimization_output.json"
SWARM_PATH = "backend/data/swarm_state.json"
LEADERBOARD_PATH = "backend/data/swarm_leaderboard.json"

def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def spawn_variants():
    opt = _load(OPT_PATH)
    variants = []

    for item in opt.get("optimized", []):
        product = item.get("product")

        for v in item.get("variants", []):
            variants.append({
                "product": product,
                "headline": v.get("headline"),
                "price": v.get("price"),
                "score": random.uniform(1, 10),
                "created_at": time.time()
            })

    return variants

def run_swarm() -> Dict[str, Any]:
    state = _load(SWARM_PATH)
    leaderboard = _load(LEADERBOARD_PATH)

    if not isinstance(leaderboard, list):
        leaderboard = []

    new_variants = spawn_variants()

    # simulate performance changes
    for v in new_variants:
        v["score"] += random.uniform(0, 5)

    leaderboard.extend(new_variants)

    # rank
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

    # prune weak
    leaderboard = leaderboard[:20]

    top = leaderboard[0] if leaderboard else {}

    output = {
        "status": "ok",
        "total_variants": len(leaderboard),
        "top_variant": top,
        "timestamp": time.time()
    }

    _save(SWARM_PATH, output)
    _save(LEADERBOARD_PATH, leaderboard)

    return output
