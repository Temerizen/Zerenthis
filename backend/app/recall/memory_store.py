import json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "backend/data/recall/memory.json"

def load():
    if DB.exists():
        return json.loads(DB.read_text())
    return []

def save(data):
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.write_text(json.dumps(data, indent=2))

def add(entry):
    data = load()
    entry["ts"] = time.time()
    data.append(entry)
    save(data)

def all():
    return load()