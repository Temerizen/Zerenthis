import os
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "backend", "data.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backend", "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def make_backup(snapshot: dict):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = {
        "timestamp": ts,
        "snapshot": snapshot
    }

    json_path = os.path.join(BACKUP_DIR, f"snapshot_{ts}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    db_copy = None
    if os.path.exists(DB_PATH):
        db_copy = os.path.join(BACKUP_DIR, f"data_{ts}.db")
        shutil.copy2(DB_PATH, db_copy)

    return {
        "json_backup": json_path,
        "db_backup": db_copy
    }

def list_backups():
    items = []
    for name in sorted(os.listdir(BACKUP_DIR), reverse=True):
        path = os.path.join(BACKUP_DIR, name)
        if os.path.isfile(path):
            items.append({
                "filename": name,
                "path": path,
                "size": os.path.getsize(path)
            })
    return items[:200]


