import json
import os
from collections import deque

DATA_DIR = "backend/data"
MEMORY_FILE = os.path.join(DATA_DIR, "performance_memory.json")
MAX_TRADES = 20

def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"trades": []}, f, indent=2)

def load_memory():
    _ensure()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        data = {"trades": []}
    if "trades" not in data or not isinstance(data["trades"], list):
        data["trades"] = []
    return data

def save_memory(mem):
    _ensure()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)

def record_trade(pnl):
    if pnl is None:
        return
    try:
        pnl = float(pnl)
    except Exception:
        return
    if abs(pnl) < 1e-9:
        return

    mem = load_memory()
    trades = deque(mem.get("trades", []), maxlen=MAX_TRADES)
    trades.append(pnl)
    mem["trades"] = list(trades)
    save_memory(mem)

def get_stats():
    mem = load_memory()
    trades = [float(x) for x in mem.get("trades", [])]

    if not trades:
        return {
            "count": 0,
            "winrate": 0.0,
            "avg_pnl": 0.0,
            "loss_streak": 0
        }

    wins = sum(1 for t in trades if t > 0)
    avg_pnl = sum(trades) / len(trades)

    loss_streak = 0
    for t in reversed(trades):
        if t < 0:
            loss_streak += 1
        else:
            break

    return {
        "count": len(trades),
        "winrate": round(wins / len(trades), 4),
        "avg_pnl": round(avg_pnl, 6),
        "loss_streak": loss_streak
    }
