from pathlib import Path
from typing import Dict, Any
from backend.app.engines.state_guard import safe_load_json, safe_save_json, normalize_memory

DATA_DIR = Path("backend/data/market")
MEMORY_FILE = DATA_DIR / "strategy_memory.json"

def load_memory() -> Dict[str, Any]:
    return normalize_memory(safe_load_json(MEMORY_FILE, {}))

def save_memory(memory: Dict[str, Any]):
    clean = normalize_memory(memory)
    safe_save_json(MEMORY_FILE, clean)

def update_memory(trades):
    memory = load_memory()
    memory["total_runs"] += 1

    for t in trades:
        asset = str(t.get("asset"))
        profit = float(t.get("profit", 0) or 0)

        if asset not in memory["assets"]:
            memory["assets"][asset] = {"wins": 0, "losses": 0, "total_profit": 0.0}

        if profit > 0:
            memory["assets"][asset]["wins"] += 1
        elif profit < 0:
            memory["assets"][asset]["losses"] += 1

        memory["assets"][asset]["total_profit"] += profit

    save_memory(memory)
    return memory

