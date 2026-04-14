from pathlib import Path
import json
import py_compile

MEMORY = Path("backend/data/execution_memory.json")
ENGINE = Path("backend/app/cognition/feedback_engine.py")

# -------------------------
# 1) ADD processed flag to old events if missing
# -------------------------
try:
    memory = json.loads(MEMORY.read_text(encoding="utf-8"))
except Exception:
    memory = {"events": []}

events = memory.get("events", [])
if isinstance(events, list):
    for ev in events:
        if isinstance(ev, dict) and "processed" not in ev:
            ev["processed"] = False

MEMORY.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")

# -------------------------
# 2) REWRITE feedback engine safely
# -------------------------
code = """from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

BASE = Path("backend/data")
MEMORY_PATH = BASE / "execution_memory.json"
IDENTITY_PATH = BASE / "identity_state.json"


def _load_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _safe_write(path: Path, data: Any):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def apply_feedback() -> Dict[str, Any]:
    memory = _load_json(MEMORY_PATH, {"events": []})
    identity = _load_json(IDENTITY_PATH, {})

    events = memory.get("events", [])
    if not isinstance(events, list):
        events = []

    prefs = identity.get("preferences", {})
    if not isinstance(prefs, dict):
        prefs = {}

    processed_count = 0

    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("processed") is True:
            continue

        task = event.get("task")
        if not task:
            event["processed"] = True
            continue

        if task not in prefs:
            prefs[task] = 1.0

        if event.get("outcome") == "success":
            prefs[task] += 0.05
        else:
            prefs[task] -= 0.05

        event["processed"] = True
        processed_count += 1

    for k in list(prefs.keys()):
        try:
            prefs[k] = round(max(0.01, min(float(prefs[k]), 50.0)), 4)
        except Exception:
            prefs[k] = 1.0

    identity["preferences"] = prefs

    _safe_write(IDENTITY_PATH, identity)
    _safe_write(MEMORY_PATH, {"events": events})

    return {
        "status": "updated",
        "processed_events": processed_count,
        "preferences": prefs
    }
"""
ENGINE.write_text(code, encoding="utf-8")
py_compile.compile(str(ENGINE), doraise=True)

print("K_HOTFIX_APPLIED")
