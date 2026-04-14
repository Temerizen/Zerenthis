import json
import os
import time
from typing import Dict, Any

DATA_PATH = "backend/data/self_model_state.json"

def _default():
    return {
        "confidence": 0.5,
        "history": [],
        "mode": "learning"
    }

def _load():
    if not os.path.exists(DATA_PATH):
        return _default()
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = _default()
        base.update(data)
        return base
    except:
        return _default()

def _save(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run(context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = _load()

    # simple adaptive confidence
    state["confidence"] = min(1.0, state["confidence"] + 0.01)

    if state["confidence"] > 0.75:
        state["mode"] = "confident"
    elif state["confidence"] > 0.6:
        state["mode"] = "adapting"
    else:
        state["mode"] = "learning"

    state["history"].append({
        "t": time.time(),
        "confidence": state["confidence"],
        "mode": state["mode"]
    })

    state["history"] = state["history"][-200:]

    _save(state)

    return state
