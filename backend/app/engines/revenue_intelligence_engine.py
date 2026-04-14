from __future__ import annotations
import json, time, os
from typing import Dict, Any, List

DATA_PATH = "backend/data/revenue_memory.json"
INTEL_PATH = "backend/data/revenue_intelligence.json"

def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(path: str, data: Dict[str, Any]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _compute_metrics(history: List[float]) -> Dict[str, float]:
    if len(history) < 2:
        return {"growth": 0, "velocity": 0, "stagnation": 1, "decay": 0, "streak": 0}

    deltas = [history[i] - history[i - 1] for i in range(1, len(history))]
    recent = deltas[-3:] if len(deltas) >= 3 else deltas

    growth = sum(recent)
    velocity = deltas[-1]
    stagnation = 1 if abs(sum(recent)) < 0.01 else 0
    decay = 1 if velocity < 0 else 0

    streak = 0
    for d in reversed(deltas):
        if d > 0:
            streak += 1
        else:
            break

    return {
        "growth": round(growth, 4),
        "velocity": round(velocity, 4),
        "stagnation": stagnation,
        "decay": decay,
        "streak": streak,
    }

def run_revenue_intelligence() -> Dict[str, Any]:
    data = _load_json(DATA_PATH)
    intel = {"products": [], "timestamp": time.time()}

    for name, info in data.items():
        if not isinstance(info, dict):
            continue

        signal = info.get("revenue", info.get("score", 0))
        history = info.get("history", [])
        if not isinstance(history, list):
            history = []

        history.append(signal)
        history = history[-10:]
        info["history"] = history

        metrics = _compute_metrics(history)

        score = float(signal)
        score += metrics["growth"] * 2
        score += metrics["velocity"] * 3
        score += metrics["streak"] * 1.5

        if metrics["stagnation"]:
            score *= 0.7
        if metrics["decay"]:
            score *= 0.8

        intel["products"].append({
            "name": name,
            "signal": round(float(signal), 4),
            "score": round(score, 4),
            "metrics": metrics,
            "times_seen": info.get("times_seen", 0),
            "price": info.get("price", 0),
        })

    intel["products"] = sorted(intel["products"], key=lambda x: x["score"], reverse=True)
    intel["dominant"] = intel["products"][0] if intel["products"] else None
    intel["at_risk"] = [
        p for p in intel["products"]
        if p["metrics"]["stagnation"] or p["metrics"]["decay"]
    ]

    _save_json(INTEL_PATH, intel)
    _save_json(DATA_PATH, data)
    return intel
