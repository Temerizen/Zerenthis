import json, os
from datetime import datetime

MEMORY_PATH = "backend/data/market_memory.json"

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(memory):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory[-200:], f, indent=2)  # keep last 200 cycles

def record_cycle(market_data, strategies, best_strategy):
    memory = load_memory()

    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "market": market_data,
        "best_strategy": best_strategy["name"],
        "top_profit": best_strategy["profit"]
    }

    memory.append(snapshot)
    save_memory(memory)

def detect_patterns():
    memory = load_memory()

    if len(memory) < 5:
        return {"pattern": "insufficient_data"}

    recent = memory[-5:]

    trend_up = sum(1 for m in recent if m["top_profit"] > 0)
    trend_down = 5 - trend_up

    if trend_up >= 4:
        return {"pattern": "bullish_streak"}
    elif trend_down >= 4:
        return {"pattern": "bearish_streak"}
    else:
        return {"pattern": "volatile"}

def get_bias(pattern):
    if pattern == "bullish_streak":
        return 1.1
    elif pattern == "bearish_streak":
        return 0.85
    else:
        return 1.0
