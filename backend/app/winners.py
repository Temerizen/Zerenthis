import json
from pathlib import Path

FILE = Path("backend/data/winners.json")

def load():
    if not FILE.exists():
        return []
    return json.loads(FILE.read_text())

def save(data):
    FILE.write_text(json.dumps(data, indent=2))

def add_winner(entry):
    data = load()
    data.append(entry)
    save(data)
