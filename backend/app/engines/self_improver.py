from __future__ import annotations
import json, os, time
from typing import Dict, Any

TRAFFIC_PATH = "backend/data/traffic_intelligence.json"
HISTORY_PATH = "backend/data/performance_history.json"
OUTPUT_PATH = "backend/data/self_improvement.json"

WINDOW = 5  # last N cycles

def _load(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run_self_improver() -> Dict[str, Any]:
    traffic = _load(TRAFFIC_PATH)
    history = _load(HISTORY_PATH)

    if not isinstance(history, dict):
        history = {}

    results = traffic.get("results", [])

    # update rolling history
    for r in results:
        name = r.get("name")
        rev = float(r.get("revenue", 0))

        history.setdefault(name, [])
        history[name].append(rev)
        history[name] = history[name][-WINDOW:]

    # compute stability metrics
    metrics = []

    for name, values in history.items():
        avg = sum(values) / max(1, len(values))
        consistency = sum(1 for v in values if v > 0) / len(values)

        metrics.append({
            "name": name,
            "avg_revenue": round(avg, 2),
            "consistency": round(consistency, 2),
            "samples": len(values)
        })

    # choose stable winner
    metrics_sorted = sorted(
        metrics,
        key=lambda x: (x["avg_revenue"], x["consistency"]),
        reverse=True
    )

    stable_winner = metrics_sorted[0] if metrics_sorted else {}

    # detect instability
    current_top = traffic.get("top_performer", {}).get("name")
    stable_name = stable_winner.get("name")

    instability = False
    if current_top and stable_name and current_top != stable_name:
        instability = True

    builder_signal = None
    if instability:
        builder_signal = "stabilize_selection_logic"

    output = {
        "status": "ok",
        "stable_winner": stable_winner,
        "current_top": current_top,
        "instability_detected": instability,
        "builder_signal": builder_signal,
        "metrics": metrics_sorted,
        "timestamp": time.time()
    }

    _save(HISTORY_PATH, history)
    _save(OUTPUT_PATH, output)

    return output
