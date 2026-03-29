from pathlib import Path
from datetime import datetime

LOG_FILE = Path("backend/self_improve/worker.log")


def log(message):
    stamp = datetime.utcnow().isoformat()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {message}\n")
