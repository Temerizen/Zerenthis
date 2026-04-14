from __future__ import annotations
import json, os, time
from typing import Dict, Any

DEMAND_PATH = "backend/data/demand_intelligence.json"
AUTO_PATH = "backend/data/auto_captured_signals.json"
CONVERSION_PATH = "backend/data/conversion_memory.json"
SCALING_PATH = "backend/data/scaling_state.json"
OUTPUT_PATH = "backend/data/real_decision.json"

def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_list(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run_real_decision() -> Dict[str, Any]:
    demand = _load(DEMAND_PATH)
    auto = _load_list(AUTO_PATH)
    conversions = _load(CONVERSION_PATH)
    scaling = _load(SCALING_PATH)

    results = demand.get("results", [])
    current = scaling.get("promoted", {})

    auto_scores = {}
    for a in auto:
        name = a.get("product")
        val = float(a.get("value", 1) or 1)
        auto_scores[name] = auto_scores.get(name, 0) + val * 1.5

    real_scores = {}
    for name, data in conversions.items():
        clicks = data.get("clicks", 0)
        real_scores[name] = clicks * 5  # STRONG weight

    combined = []

    for r in results:
        name = r.get("name")
        base = float(r.get("interest_score", 0) or 0)
        auto_boost = auto_scores.get(name, 0)
        real_boost = real_scores.get(name, 0)

        combined.append({
            "name": name,
            "interest_score": base,
            "auto_boost": round(auto_boost, 2),
            "real_boost": round(real_boost, 2),
            "final_score": round(base + auto_boost + real_boost, 2)
        })

    combined = sorted(combined, key=lambda x: x["final_score"], reverse=True)

    top = combined[0] if combined else {}
    chosen = top

    output = {
        "status": "ok",
        "final_champion": chosen.get("name"),
        "scores": combined,
        "timestamp": time.time()
    }

    _save(OUTPUT_PATH, output)
    return output
