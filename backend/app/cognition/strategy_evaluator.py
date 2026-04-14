import json
import os
from collections import defaultdict

STRATEGY_PATH = "backend/data/strategy_memory.json"

def _load():
    if not os.path.exists(STRATEGY_PATH):
        return {"sequences": []}
    try:
        with open(STRATEGY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {"sequences": []}
    except Exception:
        return {"sequences": []}

def analyze_strategies():
    data = _load()
    grouped = defaultdict(list)

    for entry in data.get("sequences", []):
        seq = entry.get("sequence")
        score = entry.get("score")
        if isinstance(seq, list) and isinstance(score, (int, float)):
            grouped[tuple(seq)].append(float(score))

    stats = {}
    for seq, scores in grouped.items():
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)
        stats[seq] = {
            "average": avg,
            "variance": variance,
            "count": len(scores),
        }
    return stats

def get_strategy_bias(current_history):
    if not isinstance(current_history, list) or len(current_history) < 3:
        return 0.0

    stats = analyze_strategies()
    key = tuple(current_history[-3:])
    data = stats.get(key)
    if not data:
        return 0.0

    avg = float(data["average"])
    variance = float(data["variance"])
    count = int(data["count"])

    stability = max(0.0, min(1.0, 1 - variance))
    confidence = min(1.0, count / 5.0)

    return avg * stability * confidence * 0.35
