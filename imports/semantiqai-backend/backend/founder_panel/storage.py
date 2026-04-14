import json
from datetime import datetime
from pathlib import Path
from backend.platform.paths import BACKEND_DIR

DATA_DIR = BACKEND_DIR / "founder_panel"
STATE_PATH = DATA_DIR / "state.json"
LOG_PATH = DATA_DIR / "action_log.json"

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
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_state():
    state = _read_json(STATE_PATH, DEFAULT_STATE)
    if not STATE_PATH.exists():
        _write_json(STATE_PATH, state)
    return state

def save_state(state):
    _write_json(STATE_PATH, state)

def get_logs():
    logs = _read_json(LOG_PATH, [])
    if not LOG_PATH.exists():
        _write_json(LOG_PATH, logs)
    return logs

def append_log(action, payload=None):
    logs = get_logs()
    logs.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "payload": payload or {}
    })
    _write_json(LOG_PATH, logs[-500:])
    return logs[-1]
