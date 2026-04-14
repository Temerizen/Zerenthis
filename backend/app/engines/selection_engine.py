from __future__ import annotations
import json
from pathlib import Path

DATA_PATH = Path("backend/data/revenue_memory.json")

def _load():
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {}

def select_winners(top_n: int = 1):
    data = _load()
    if not data:
        return []

    ranked = sorted(
        data.items(),
        key=lambda x: x[1].get("score", 0),
        reverse=True
    )

    winners = [name for name, _ in ranked[:top_n]]
    return winners

def prune_losers(min_score: float = 1.0):
    data = _load()
    new_data = {
        k: v for k, v in data.items()
        if v.get("score", 0) >= min_score
    }

    DATA_PATH.write_text(json.dumps(new_data, indent=2), encoding="utf-8")
    return new_data
