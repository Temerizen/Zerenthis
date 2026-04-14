import json
from datetime import datetime
from pathlib import Path
from backend.platform.paths import BACKEND_DIR

LOG_PATH = BACKEND_DIR / "stabilization" / "logs.json"

def log_event(event, data=None):
    entry = {
        "time": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "data": data or {}
    }

    logs = []
    if LOG_PATH.exists():
        try:
            logs = json.loads(LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            logs = []

    logs.append(entry)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(logs[-500:], indent=2, ensure_ascii=False), encoding="utf-8")

    return entry
