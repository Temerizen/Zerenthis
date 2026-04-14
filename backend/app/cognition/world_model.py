import json
import os
import time
from typing import Dict, Any

DATA_PATH = "backend/data/world_model.json"

def _default():
    return {
        "patterns": [],
        "history": []
    }

def _load():
    if not os.path.exists(DATA_PATH):
        return _default()
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = _default()
        if isinstance(data, dict):
            base.update(data)
        return base
    except Exception:
        return _default()

def _save(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _safe_signal_extract(data: Dict[str, Any]) -> int:
    try:
        if isinstance(data, dict):
            if isinstance(data.get("world"), dict):
                return int(data["world"].get("signals", 0))
            if isinstance(data.get("result"), dict):
                if isinstance(data["result"].get("world"), dict):
                    return int(data["result"]["world"].get("signals", 0))
    except Exception:
        pass
    return 0

def run(context: Dict[str, Any]) -> Dict[str, Any]:
    state = _load()

    signal_value = _safe_signal_extract(context)

    entry = {
        "t": time.time(),
        "signal": signal_value
    }

    state["history"].append(entry)

    if len(state["history"]) >= 3:
        last3 = [h.get("signal", 0) for h in state["history"][-3:]]
        state["patterns"].append(last3)

    state["history"] = state["history"][-200:]
    state["patterns"] = state["patterns"][-100:]

    _save(state)

    return {
        "status": "ok",
        "signal": signal_value,
        "patterns": len(state["patterns"])
    }
