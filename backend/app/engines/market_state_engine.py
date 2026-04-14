from pathlib import Path
from typing import Dict, Any
from backend.app.engines.state_guard import safe_load_json, safe_save_json, normalize_market_state

DATA_DIR = Path("backend/data/market")
STATE_FILE = DATA_DIR / "state.json"

def load_market_state() -> Dict[str, Any]:
    return normalize_market_state(safe_load_json(STATE_FILE, {}))

def save_market_state(state: Dict[str, Any]) -> Dict[str, Any]:
    clean = normalize_market_state(state)
    return safe_save_json(STATE_FILE, clean)

