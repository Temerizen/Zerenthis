from pathlib import Path
from typing import Dict, Any
from backend.app.engines.state_guard import safe_load_json, safe_save_json, normalize_strategy_board, normalize_strategy_row

DATA_DIR = Path("backend/data/market")
LEADERBOARD_FILE = DATA_DIR / "strategy_leaderboard.json"

def load_strategy_board() -> Dict[str, Any]:
    return normalize_strategy_board(safe_load_json(LEADERBOARD_FILE, {}))

def save_strategy_board(board: Dict[str, Any]):
    clean = normalize_strategy_board(board)
    safe_save_json(LEADERBOARD_FILE, clean)

def update_strategy_board(results: Dict[str, Any], best_strategy: str):
    board = load_strategy_board()

    for name, stats in (results or {}).items():
        row = normalize_strategy_row(board["strategies"].get(name, {}))
        row["runs"] += 1
        row["total_profit"] += float(stats.get("profit", 0) or 0)
        row["total_trades"] += int(stats.get("trades", 0) or 0)
        row["wins"] += int(stats.get("wins", 0) or 0)
        row["losses"] += int(stats.get("losses", 0) or 0)
        row["last_profit"] = float(stats.get("profit", 0) or 0)
        row["avg_profit"] = round(row["total_profit"] / max(row["runs"], 1), 4)
        row["avg_winrate"] = round((row["wins"] / max(row["total_trades"], 1)) * 100, 2)
        board["strategies"][name] = row

    board["last_best_strategy"] = best_strategy
    save_strategy_board(board)
    return board

