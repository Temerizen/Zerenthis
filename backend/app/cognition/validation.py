from __future__ import annotations
import json, time, tempfile, subprocess
from pathlib import Path

PATH = Path("backend/data/validation_state.json")
APPLY_PATH = Path("backend/data/apply_state.json")

def _default():
    return {
        "history": [],
        "passed": 0,
        "failed": 0,
        "last_result": None
    }

def _load():
    if not PATH.exists():
        return _default()
    try:
        return json.loads(PATH.read_text())
    except:
        return _default()

def _load_apply():
    if not APPLY_PATH.exists():
        return None
    try:
        return json.loads(APPLY_PATH.read_text())
    except:
        return None

def _save(d):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(d, indent=2))

def _validate(plan):
    target = Path(plan["target"])
    if not target.exists():
        return {"valid": False, "reason": "missing_target"}

    content = target.read_text(encoding="utf-8", errors="ignore").lstrip("\ufeff")
    test = content + "\n" + plan["change"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(test.encode("utf-8"))
        tmp_path = tmp.name

    r = subprocess.run(["python","-m","py_compile",tmp_path],capture_output=True,text=True)

    if r.returncode != 0:
        return {"valid": False, "reason": "compile_error", "error": r.stderr[-300:]}

    return {"valid": True, "reason": "safe_patch"}

def run(_=None):
    state = _load()
    apply_data = _load_apply()

    if not apply_data or not apply_data.get("active_plan"):
        return {"status": "no_active_plan"}

    plan = apply_data["active_plan"]

    result = _validate(plan)

    record = {
        "timestamp": time.time(),
        "plan": plan,
        "validation": result
    }

    state["history"].append(record)
    state["history"] = state["history"][-200:]
    state["last_result"] = record

    if result["valid"]:
        state["passed"] += 1
    else:
        state["failed"] += 1

    _save(state)

    return {
        "status": "validated",
        "valid": result["valid"],
        "reason": result["reason"]
    }

def state():
    return _load()
