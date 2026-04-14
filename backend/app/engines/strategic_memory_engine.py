from __future__ import annotations
import json, os, time
from typing import Dict, Any, List

INTEL_PATH = "backend/data/revenue_intelligence.json"
MUTATION_PATH = "backend/data/mutation_output.json"
MEMORY_PATH = "backend/data/strategic_memory.json"

def _load(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _price_band(price: float) -> str:
    if price < 20:
        return "low"
    if price < 40:
        return "mid"
    return "high"

def _infer_angle(name: str, headline: str = "") -> str:
    text = f"{name} {headline}".lower()
    if "premium" in text or "pro" in text or "advanced" in text:
        return "premium"
    if "lite" in text or "beginner" in text or "simple" in text:
        return "simplicity"
    if "fast" in text or "speed" in text:
        return "speed"
    if "auto" in text or "automation" in text:
        return "automation"
    return "general"

def _ensure_bucket(memory: Dict[str, Any], key: str):
    if key not in memory:
        memory[key] = {
            "wins": 0,
            "appearances": 0,
            "total_score": 0.0,
            "avg_score": 0.0,
        }

def _update_bucket(memory: Dict[str, Any], key: str, score: float, won: bool):
    _ensure_bucket(memory, key)
    bucket = memory[key]
    bucket["appearances"] += 1
    bucket["total_score"] += float(score)
    if won:
        bucket["wins"] += 1
    bucket["avg_score"] = round(bucket["total_score"] / max(1, bucket["appearances"]), 4)

def run_strategic_memory() -> Dict[str, Any]:
    intel = _load(INTEL_PATH)
    mutation = _load(MUTATION_PATH)
    memory = _load(MEMORY_PATH)

    if not isinstance(memory, dict):
        memory = {}

    memory.setdefault("angles", {})
    memory.setdefault("price_bands", {})
    memory.setdefault("types", {})
    memory.setdefault("dominant_history", [])
    memory.setdefault("runs", 0)
    memory.setdefault("last_updated", None)

    products = intel.get("products", [])
    dominant = intel.get("dominant") or {}

    dominant_name = dominant.get("name", "")
    dominant_score = float(dominant.get("score", 0) or 0)

    clone_names = set()
    mutation_names = set()

    for item in mutation.get("clones", []):
        if isinstance(item, dict) and item.get("name"):
            clone_names.add(item["name"])

    for item in mutation.get("mutations", []):
        if isinstance(item, dict) and item.get("name"):
            mutation_names.add(item["name"])

    for p in products:
        if not isinstance(p, dict):
            continue

        name = p.get("name", "Unknown")
        score = float(p.get("score", 0) or 0)
        price = float(p.get("price", 0) or 0)
        won = name == dominant_name

        ptype = "organic"
        if name in clone_names:
            ptype = "clone"
        elif name in mutation_names:
            ptype = "mutation"

        angle = _infer_angle(name, p.get("headline", ""))
        band = _price_band(price)

        _update_bucket(memory["angles"], angle, score, won)
        _update_bucket(memory["price_bands"], band, score, won)
        _update_bucket(memory["types"], ptype, score, won)

    if dominant_name:
        memory["dominant_history"].append({
            "name": dominant_name,
            "score": dominant_score,
            "timestamp": time.time(),
        })
        memory["dominant_history"] = memory["dominant_history"][-25:]

    memory["runs"] += 1
    memory["last_updated"] = time.time()

    def top_bucket(section: Dict[str, Any]) -> Dict[str, Any]:
        if not section:
            return {}
        ranked = sorted(
            section.items(),
            key=lambda kv: (kv[1].get("wins", 0), kv[1].get("avg_score", 0)),
            reverse=True
        )
        return {
            "name": ranked[0][0],
            **ranked[0][1]
        }

    result = {
        "status": "ok",
        "runs": memory["runs"],
        "best_angle": top_bucket(memory["angles"]),
        "best_price_band": top_bucket(memory["price_bands"]),
        "best_type": top_bucket(memory["types"]),
        "current_dominant": dominant_name,
        "dominant_history_count": len(memory["dominant_history"]),
        "memory": memory,
    }

    _save(MEMORY_PATH, memory)
    return result
