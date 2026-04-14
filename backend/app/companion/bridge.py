from pathlib import Path
import json
import time

BASE = Path(__file__).resolve().parent

PATCH_DIR = BASE / "data" / "patch_plans"

def get_latest_patch():
    if not PATCH_DIR.exists():
        return None
    files = sorted(PATCH_DIR.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0] if files else None

def read_patch():
    patch = get_latest_patch()
    if not patch:
        return None
    return patch.read_text(encoding="utf-8")

def system_snapshot():
    return {
        "time": time.time(),
        "patch_available": get_latest_patch() is not None
    }

def decide():
    snapshot = system_snapshot()
    if snapshot["patch_available"]:
        return "apply_patch"
    return "observe"

def run():
    decision = decide()
    return {
        "decision": decision,
        "snapshot": system_snapshot()
    }

if __name__ == "__main__":
    print(run())

