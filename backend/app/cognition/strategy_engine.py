import json
import os
import time
from typing import List, Dict, Any

STRATEGY_PATH = "backend/data/strategy_memory.json"

MAX_SEQUENCE_LENGTH = 3
MAX_MEMORY = 200

def _safe_load():
    if not os.path.exists(STRATEGY_PATH):
        return {"sequences": []}
    try:
        with open(STRATEGY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {"sequences": []}
    except:
        return {"sequences": []}

def _safe_save(data):
    os.makedirs(os.path.dirname(STRATEGY_PATH), exist_ok=True)
    with open(STRATEGY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def record_sequence(history: List[str], outcome: float):
    data = _safe_load()

    if len(history) < MAX_SEQUENCE_LENGTH:
        return

    seq = history[-MAX_SEQUENCE_LENGTH:]

    entry = {
        "sequence": seq,
        "score": outcome,
        "timestamp": time.time()
    }

    data["sequences"].append(entry)

    if len(data["sequences"]) > MAX_MEMORY:
        data["sequences"] = data["sequences"][-MAX_MEMORY:]

    _safe_save(data)

def get_sequence_bonus(current_history: List[str]) -> float:
    data = _safe_load()
    if len(current_history) < MAX_SEQUENCE_LENGTH:
        return 0.0

    recent = current_history[-MAX_SEQUENCE_LENGTH:]

    bonus = 0.0

    for entry in data["sequences"]:
        if entry["sequence"] == recent:
            bonus += entry["score"] * 0.1  # soft reinforcement

    return bonus
