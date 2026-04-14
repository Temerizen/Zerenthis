import json
from pathlib import Path
from backend.platform.paths import BACKEND_DIR

def get_path(name):
    return BACKEND_DIR / name / "data.json"

def read(name):
    path = get_path(name)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return {}

def write(name, data):
    path = get_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

