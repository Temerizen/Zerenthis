from __future__ import annotations
import json, os, time
from typing import Dict, Any, List

OPT_PATH = "backend/data/optimization_output.json"
VAR_TRACK_PATH = "backend/data/variant_tracking.json"
VAR_CONV_PATH = "backend/data/variant_conversions.json"
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

def _ensure_variant_links():
    from backend.app.engines.variant_tracking_engine import generate_variant_link
    opt = _load(OPT_PATH)
    links = []

    for item in opt.get("optimized", []):
        product = item.get("product")
        for v in item.get("variants", []):
            links.append(generate_variant_link(product, v.get("headline")))
    return links

def run_real_swarm() -> Dict[str, Any]:
    _ensure_variant_links()

    conv = _load(VAR_CONV_PATH)
    leaderboard = []

    # build leaderboard from REAL clicks
    now = time.time()
    for key, v in conv.items():
        clicks = v.get("clicks", 0)
        last = v.get("last_click") or now

        # recency boost (newer clicks matter slightly more)
        age_sec = max(1.0, now - last)
        recency = max(0.5, min(2.0, 3600.0 / age_sec))  # between 0.5 and 2.0

        score = round(clicks * recency, 3)

        leaderboard.append({
            "product": v.get("product"),
            "headline": v.get("headline"),
            "clicks": clicks,
            "recency": round(recency, 3),
            "score": score,
            "last_click": last
        })

    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

    # prune to top 20
    leaderboard = leaderboard[:20]

    top = leaderboard[0] if leaderboard else {}

    out = {
        "status": "ok",
        "total_variants": len(leaderboard),
        "top_variant": top,
        "timestamp": now
    }

    _save(LEADERBOARD_PATH, leaderboard)
    return out
