from __future__ import annotations
import json, os, time, random
from typing import Dict, Any

INTEL_PATH = "backend/data/revenue_intelligence.json"
TRAFFIC_PATH = "backend/data/traffic_intelligence.json"

def _load(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def simulate_traffic(product: Dict[str, Any]) -> Dict[str, Any]:
    base = product.get("score", 1)

    impressions = int(random.uniform(50, 200) * (base / 10))
    clicks = int(impressions * random.uniform(0.05, 0.15))
    conversions = int(clicks * random.uniform(0.05, 0.2))

    revenue = conversions * float(product.get("price", 10))

    return {
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "revenue": revenue
    }

def run_traffic_intelligence() -> Dict[str, Any]:
    intel = _load(INTEL_PATH)

    products = intel.get("products", [])

    results = []
    best = None

    for p in products:
        if not isinstance(p, dict):
            continue

        traffic = simulate_traffic(p)

        entry = {
            "name": p.get("name"),
            "score": p.get("score"),
            "price": p.get("price"),
            **traffic
        }

        results.append(entry)

        if not best or entry["revenue"] > best["revenue"]:
            best = entry

    output = {
        "status": "ok",
        "results": sorted(results, key=lambda x: x["revenue"], reverse=True),
        "top_performer": best,
        "timestamp": time.time()
    }

    _save(TRAFFIC_PATH, output)
    return output
