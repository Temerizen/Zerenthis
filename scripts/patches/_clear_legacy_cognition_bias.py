from pathlib import Path
import json
import time

IDENTITY = Path("backend/data/identity_state.json")
THOUGHTS = Path("backend/data/thought_stream.json")
REFLECTIONS = Path("backend/data/reflections.json")
BACKUP_DIR = Path("backend/data/_cognition_backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def read_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

stamp = int(time.time())

identity = read_json(IDENTITY, {})
thoughts = read_json(THOUGHTS, [])
reflections = read_json(REFLECTIONS, [])

write_json(BACKUP_DIR / f"identity_state.{stamp}.json", identity)
write_json(BACKUP_DIR / f"thought_stream.{stamp}.json", thoughts)
write_json(BACKUP_DIR / f"reflections.{stamp}.json", reflections)

# 1. Remove legacy loop-level preference/history bias
if isinstance(identity, dict):
    prefs = identity.get("preferences", {})
    if isinstance(prefs, dict) and "execute_all" in prefs:
        del prefs["execute_all"]

    history = identity.get("history", {})
    if isinstance(history, dict):
        repeated = history.get("repeated_tasks", {})
        if isinstance(repeated, dict) and "execute_all" in repeated:
            del repeated["execute_all"]

    if identity.get("last_task") == "execute_all":
        identity["last_task"] = "legacy_cleared"

    beliefs = identity.get("beliefs", [])
    if isinstance(beliefs, list):
        identity["beliefs"] = [b for b in beliefs if "execute_all" not in str(b)]

# 2. Keep thought history, but mark legacy loop-level thoughts as legacy
if isinstance(thoughts, list):
    for item in thoughts:
        if isinstance(item, dict) and item.get("chosen_task") == "execute_all":
            extra = item.get("extra", {})
            if not isinstance(extra, dict):
                extra = {}
            extra["legacy_loop_level_entry"] = True
            item["extra"] = extra

# 3. Clear stale reflections so new task-aware reflections can rebuild cleanly
if isinstance(reflections, list):
    reflections = []

write_json(IDENTITY, identity)
write_json(THOUGHTS, thoughts)
write_json(REFLECTIONS, reflections)

print("LEGACY_COGNITION_BIAS_CLEARED")
