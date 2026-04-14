from pathlib import Path
from backend.app.engines.state_guard import safe_load_json, safe_save_json, normalize_trade_history

BASE = Path("backend/data")
HISTORY_FILE = BASE / "trades_history.json"

def load_history():
    return normalize_trade_history(safe_load_json(HISTORY_FILE, []))

def save_trade(trade):
    history = load_history()
    history.append(trade)
    safe_save_json(HISTORY_FILE, history)

def get_stats():
    history = load_history()
    if not history:
        return {"trades": 0, "total_profit": 0.0, "wins": 0, "losses": 0, "winrate": 0.0}

    total = sum(float(t.get("profit", 0) or 0) for t in history)
    wins = sum(1 for t in history if float(t.get("profit", 0) or 0) > 0)
    losses = sum(1 for t in history if float(t.get("profit", 0) or 0) <= 0)

    return {
        "trades": len(history),
        "total_profit": round(total, 4),
        "wins": wins,
        "losses": losses,
        "winrate": round((wins / max(1, len(history))) * 100, 2)
    }
