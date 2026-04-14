import json
from pathlib import Path
from backend.platform.paths import BACKEND_DIR

DATA_PATH = BACKEND_DIR / "execution_engine" / "data.json"

def load_data():
    if not DATA_PATH.exists():
        return {}
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_data(data):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_user(user_id):
    data = load_data()
    return data.get(user_id, {
        "goals": [],
        "tasks": [],
        "habits": [],
        "score": 0
    })

def update_user(user_id, user_data):
    data = load_data()
    data[user_id] = user_data
    save_data(data)
