from __future__ import annotations
import json, time, os, random
from typing import Dict, Any, List

INTEL_PATH = "backend/data/revenue_intelligence.json"
MUTATION_PATH = "backend/data/mutation_output.json"

def _load(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def mutate_product(p: Dict[str, Any]) -> Dict[str, Any]:
    name = p.get("name", "Product")
    price = float(p.get("price", 19) or 19)

    angles = ["premium", "speed", "simplicity", "automation", "beginner", "advanced"]
    angle = random.choice(angles)
    new_price = round(max(5, price * random.uniform(0.7, 1.3)), 2)

    return {
        "name": f"{name} v2",
        "price": new_price,
        "headline": f"{angle.title()} version of {name} designed to increase conversions",
        "source": name,
        "type": "mutation",
    }

def clone_winner(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    base = p.get("name", "Product")
    price = float(p.get("price", 19) or 19)
    variants = ["Pro", "Lite", "Advanced"]

    return [
        {
            "name": f"{base} {v}",
            "price": price,
            "headline": f"{v} version of {base} optimized for performance",
            "source": base,
            "type": "clone",
        }
        for v in variants
    ]

def run_mutation_engine() -> Dict[str, Any]:
    intel = _load(INTEL_PATH)

    dominant = intel.get("dominant")
    at_risk = intel.get("at_risk", [])

    output = {
        "status": "ok",
        "mutations": [],
        "clones": [],
        "pruned": [],
        "timestamp": time.time(),
    }

    for p in at_risk:
        if isinstance(p, dict):
            output["mutations"].append(mutate_product(p))
            output["pruned"].append(p.get("name"))

    if isinstance(dominant, dict) and dominant:
        output["clones"] = clone_winner(dominant)

    _save(MUTATION_PATH, output)
    return output
