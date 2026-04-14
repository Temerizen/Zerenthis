import json
from pathlib import Path
from backend.platform.paths import BACKEND_DIR

DB_PATH = BACKEND_DIR / "auth_system" / "users.json"

def load_users():
    if not DB_PATH.exists():
        return {}
    try:
        return json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_users(data):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
