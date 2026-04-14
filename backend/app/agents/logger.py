import os
import json
from datetime import datetime

LOG_PATH = "backend/stabilization/logs.json"

def log_event(event, data=None):
    entry = {
        "time": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "data": data or {}
    }

    logs = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r") as f:
                logs = json.load(f)
        except:
            logs = []

    logs.append(entry)

    with open(LOG_PATH, "w") as f:
        json.dump(logs[-500:], f, indent=2)

    return entry

