import json
import os
from datetime import datetime

DATA_DIR = os.path.join("backend", "founder_panel")
STATE_PATH = os.path.join(DATA_DIR, "state.json")
LOG_PATH = os.path.join(DATA_DIR, "action_log.json")

DEFAULT_STATE = {
    "feature_toggles": {
        "cognitive_lab": True,
        "ai_school": True,
        "execution_engine": True,
        "simulation_engine": True,
        "creation_engine": True,
        "founder_video": True,
        "founder_distribution": True
    },
    "system_mode": "ascension",
    "maintenance_mode": False,
    "founder_notes": "",
    "module_registry": []
}

def _read_json(path, fallback):
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback

def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_state():
    state = _read_json(STATE_PATH, DEFAULT_STATE)
    if not os.path.exists(STATE_PATH):
        _write_json(STATE_PATH, state)
    return state

def save_state(state):
    _write_json(STATE_PATH, state)

def get_logs():
    logs = _read_json(LOG_PATH, [])
    if not os.path.exists(LOG_PATH):
        _write_json(LOG_PATH, logs)
    return logs

def append_log(action, payload=None):
    logs = get_logs()
    logs.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "payload": payload or {}
    })
    _write_json(LOG_PATH, logs)
    return logs[-1]

