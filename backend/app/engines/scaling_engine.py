from __future__ import annotations
import json, os, time
from typing import Dict, Any, List

TRAFFIC_PATH = "backend/data/traffic_intelligence.json"
MUTATION_PATH = "backend/data/mutation_output.json"
SCALING_PATH = "backend/data/scaling_state.json"

def _load(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run_scaling_engine() -> Dict[str, Any]:
    traffic = _load(TRAFFIC_PATH)
    mutation = _load(MUTATION_PATH)

    results = traffic.get("results", [])
    top = traffic.get("top_performer", {})

    clones = mutation.get("clones", [])

    promote = top if top else None

    # identify weak products
    weak = []
    for r in results:
        if r.get("revenue", 0) <= 0:
            weak.append(r.get("name"))

    # build next cycle queue
    queue: List[Dict[str, Any]] = []

    if promote:
        queue.append({
            "type": "champion",
            "data": promote
        })

    for c in clones:
        queue.append({
            "type": "expansion",
            "data": c
        })

    output = {
        "status": "ok",
        "promoted": promote,
        "expanding": [c.get("name") for c in clones],
        "pruned_candidates": weak,
        "next_cycle_queue": queue,
        "queue_size": len(queue),
        "timestamp": time.time()
    }

    _save(SCALING_PATH, output)
    return output
