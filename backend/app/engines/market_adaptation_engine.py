import json
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path("backend/data/market")
STATS_FILE = DATA_DIR / "strategy_stats.json"

DEFAULT_STATS = {
    "assets": {},
    "signals": {},
    "total_runs": 0
}

def load_stats() -> Dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if STATS_FILE.exists():
        try:
            return json.loads(STATS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return DEFAULT_STATS.copy()
    return DEFAULT_STATS.copy()

def save_stats(stats: Dict[str, Any]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATS_FILE.write_text(json.dumps(stats, indent=2), encoding="utf-8")

def update_stats(trades):
    stats = load_stats()
    stats["total_runs"] += 1

    for t in trades:
        asset = t.get("asset")
        profit = float(t.get("profit", 0))
        action = t.get("action")

        # Asset tracking
        if asset not in stats["assets"]:
            stats["assets"][asset] = {"wins": 0, "losses": 0}

        if profit > 0:
            stats["assets"][asset]["wins"] += 1
        elif profit < 0:
            stats["assets"][asset]["losses"] += 1

        # Signal tracking
        if action not in stats["signals"]:
            stats["signals"][action] = {"wins": 0, "losses": 0}

        if profit > 0:
            stats["signals"][action]["wins"] += 1
        elif profit < 0:
            stats["signals"][action]["losses"] += 1

    save_stats(stats)
    return stats

def get_bias(asset: str, action: str) -> float:
    stats = load_stats()

    asset_data = stats["assets"].get(asset, {})
    signal_data = stats["signals"].get(action, {})

    def score(data):
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        total = wins + losses
        if total == 0:
            return 1.0
        return wins / total

    asset_score = score(asset_data)
    signal_score = score(signal_data)

    # Combine both biases
    combined = (asset_score + signal_score) / 2

    # Normalize around 1.0
    return 0.5 + combined

