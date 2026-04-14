import json
from pathlib import Path
from .config import DATA_DIR

def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def read_json(relative_path: str, fallback):
    path = DATA_DIR / relative_path
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write_json(relative_path: str, data):
    path = DATA_DIR / relative_path
    ensure_parent(path)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)

def append_json_list(relative_path: str, entry, limit=1000):
    items = read_json(relative_path, [])
    if not isinstance(items, list):
        items = []
    items.append(entry)
    write_json(relative_path, items[-limit:])
    return items[-1]

def path_for(relative_path: str):
    path = DATA_DIR / relative_path
    ensure_parent(path)
    return str(path)
