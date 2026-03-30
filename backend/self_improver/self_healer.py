from __future__ import annotations
import time, shutil, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "backend" / "data" / "self_improver"
BACKUPS = DATA / "backups"
LOG = DATA / "self_heal_log.json"

CORE_FILES = [
    ROOT / "backend/self_improver/engine.py",
    ROOT / "backend/self_improver/worker.py",
    ROOT / "backend/self_improver/brain/ai_brain.py",
    ROOT / "backend/app/main.py",
]

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

def log(event):
    data = []
    if LOG.exists():
        try:
            data = json.loads(LOG.read_text())
        except:
            pass
    data.append(event)
    LOG.write_text(json.dumps(data, indent=2))

def latest_backup(file: Path):
    backups = sorted(BACKUPS.glob(f"*{file.name}.bak"), reverse=True)
    return backups[0] if backups else None

def is_valid_python(file: Path):
    try:
        compile(file.read_text(encoding="utf-8"), str(file), "exec")
        return True
    except Exception:
        return False

def heal_file(file: Path):
    backup = latest_backup(file)
    if not backup:
        print("No backup for:", file.name)
        return

    shutil.copy2(backup, file)
    log({
        "time": int(time.time()),
        "file": str(file),
        "action": "restored_from_backup",
        "backup": str(backup)
    })
    print("Healed:", file.name)

def run():
    print("Self-healer started.")
    while True:
        for file in CORE_FILES:
            if not file.exists():
                continue

            if not is_valid_python(file):
                print("Detected corruption in:", file.name)
                heal_file(file)

        time.sleep(10)

if __name__ == "__main__":
    run()

