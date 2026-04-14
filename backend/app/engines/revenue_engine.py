from __future__ import annotations
import json
from pathlib import Path

DATA_PATH = Path("backend/data/revenue_memory.json")

def _load() -> dict:
    if DATA_PATH.exists():
        try:
            return json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save(data: dict) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def record_result(products: list) -> dict:
    data = _load()

    for p in products:
        name = p.get("name", "unknown")
        price = p.get("price", 0)

        if name not in data:
            data[name] = {
                "times_seen": 0,
                "score": 0.0,
                "price": price
            }

        data[name]["times_seen"] += 1
        data[name]["score"] += float(price) * 0.1
        data[name]["price"] = price

    _save(data)
    return data
