from __future__ import annotations
import json
from pathlib import Path

VARIANT_MEMORY_PATH = Path("backend/data/variant_battle.json")

def _load() -> dict:
    if VARIANT_MEMORY_PATH.exists():
        try:
            return json.loads(VARIANT_MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save(data: dict) -> None:
    VARIANT_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VARIANT_MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def generate_offer_variants(goal: str) -> list[dict]:
    goal = (goal or "Increase conversions and revenue").strip()

    return [
        {
            "name": "Urgency Offer",
            "headline": f"{goal} with a limited-time action plan",
            "price": 19,
            "angle": "urgency",
        },
        {
            "name": "Premium Offer",
            "headline": f"{goal} with a premium done-for-you pack",
            "price": 49,
            "angle": "premium",
        },
        {
            "name": "Beginner Offer",
            "headline": f"{goal} with a simple beginner-friendly starter kit",
            "price": 9,
            "angle": "beginner",
        },
    ]

def score_variant(variant: dict) -> float:
    price = float(variant.get("price", 0))
    angle = variant.get("angle", "")

    angle_bonus = {
        "urgency": 1.2,
        "premium": 1.35,
        "beginner": 1.0,
    }.get(angle, 1.0)

    score = round(price * angle_bonus, 2)
    return score

def run_variant_battle(goal: str) -> dict:
    variants = generate_offer_variants(goal)

    scored = []
    for variant in variants:
        entry = dict(variant)
        entry["score"] = score_variant(variant)
        scored.append(entry)

    scored.sort(key=lambda x: x["score"], reverse=True)
    winner = scored[0] if scored else {}

    data = _load()
    data["last_goal"] = goal
    data["variants"] = scored
    data["winner"] = winner
    _save(data)

    return {
        "status": "ok",
        "goal": goal,
        "variants": scored,
        "winner": winner,
    }
