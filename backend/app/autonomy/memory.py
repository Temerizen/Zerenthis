import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MEM = ROOT / "backend/data/memory/memory.json"

def load():
    if MEM.exists():
        return json.loads(MEM.read_text())
    return []

def save(data):
    MEM.parent.mkdir(parents=True, exist_ok=True)
    MEM.write_text(json.dumps(data, indent=2))

def add(entry):
    data = load()
    data.append(entry)
    save(data)

def recent(n=5):
    return load()[-n:]
