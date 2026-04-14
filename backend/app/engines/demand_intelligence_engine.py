from __future__ import annotations
import json, os, time, random
from typing import Dict, Any, List

TRAFFIC_PATH = "backend/data/traffic_intelligence.json"
DEMAND_PATH = "backend/data/demand_intelligence.json"
DEMAND_HISTORY_PATH = "backend/data/demand_history.json"

def _load(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _simulate_interest(product: Dict[str, Any]) -> Dict[str, Any]:
    impressions = int(product.get("impressions", 0) or 0)
    clicks = int(product.get("clicks", 0) or 0)
    conversions = int(product.get("conversions", 0) or 0)
    score = float(product.get("score", 0) or 0)

    # No-money validation signals
    saves = int(max(0, clicks * random.uniform(0.1, 0.5)))
    waitlist_signups = int(max(0, clicks * random.uniform(0.05, 0.3)))
    replies = int(max(0, clicks * random.uniform(0.03, 0.2)))

    interest_score = round(
        (clicks * 1.0) +
        (saves * 1.5) +
        (waitlist_signups * 3.0) +
        (replies * 2.0) +
        (conversions * 4.0) +
        (score * 0.5),
        2
    )

    ctr = round((clicks / impressions), 4) if impressions > 0 else 0.0

    return {
        "impressions": impressions,
        "clicks": clicks,
        "ctr": ctr,
        "saves": saves,
        "waitlist_signups": waitlist_signups,
        "replies": replies,
        "interest_score": interest_score,
    }

def run_demand_intelligence() -> Dict[str, Any]:
    traffic = _load(TRAFFIC_PATH)
    history = _load(DEMAND_HISTORY_PATH)
    if not isinstance(history, dict):
        history = {}

    results = traffic.get("results", [])
    enriched: List[Dict[str, Any]] = []

    for item in results:
        if not isinstance(item, dict):
            continue

        name = item.get("name", "Unknown")
        signals = _simulate_interest(item)

        row = {
            "name": name,
            "score": item.get("score", 0),
            "price": item.get("price", 0),
            **signals,
            "timestamp": time.time(),
        }
        enriched.append(row)

        history.setdefault(name, [])
        history[name].append({
            "interest_score": row["interest_score"],
            "clicks": row["clicks"],
            "waitlist_signups": row["waitlist_signups"],
            "timestamp": row["timestamp"],
        })
        history[name] = history[name][-10:]

    enriched = sorted(enriched, key=lambda x: x["interest_score"], reverse=True)
    top = enriched[0] if enriched else None

    at_risk = [x for x in enriched if x["clicks"] <= 0 or x["interest_score"] <= 1]

    output = {
        "status": "ok",
        "mode": "no_money_validation",
        "results": enriched,
        "top_interest": top,
        "at_risk": at_risk,
        "timestamp": time.time(),
    }

    _save(DEMAND_PATH, output)
    _save(DEMAND_HISTORY_PATH, history)
    return output
