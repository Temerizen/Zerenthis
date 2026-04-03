import json
from pathlib import Path

DATA_FILE = Path("backend/data/files.json")

def load_files():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())

def save_files(files):
    DATA_FILE.write_text(json.dumps(files, indent=2))

def add_file(entry):
    files = load_files()
    files.append(entry)
    save_files(files)
