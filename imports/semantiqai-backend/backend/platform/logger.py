import json
from datetime import datetime
from pathlib import Path
from .config import LOG_DIR, Settings

LOG_FILE = LOG_DIR / "platform_log.json"

def _read():
    if not LOG_FILE.exists():
        return []
    try:
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def log_event(event: str, data=None, level: str = "info"):
    if not Settings.ENABLE_LOGGING:
        return {"logging": "disabled"}

    logs = _read()
    entry = {
        "time": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "event": event,
        "data": data or {}
    }
    logs.append(entry)
    LOG_FILE.write_text(json.dumps(logs[-1000:], indent=2, ensure_ascii=False), encoding="utf-8")
    return entry
