from pathlib import Path
import py_compile

p = Path("backend/app/cognition/execution_memory.py")
code = p.read_text(encoding="utf-8")

if "IDENTITY_PATH = BASE / \"identity_state.json\"" not in code:
    code = code.replace(
        'PLAN_PATH = BASE / "active_plan.json"',
        'PLAN_PATH = BASE / "active_plan.json"\nIDENTITY_PATH = BASE / "identity_state.json"'
    )

old = """    memory["events"].append(event)
    memory["events"] = memory["events"][-200:]  # cap memory

    _safe_write(EXECUTION_LOG, memory)

    return {"status": "recorded", "event": event}"""

new = """    memory["events"].append(event)
    memory["events"] = memory["events"][-200:]  # cap memory

    identity = _load_json(IDENTITY_PATH, {})
    history = identity.setdefault("history", {})
    history["successes"] = int(history.get("successes", 0) or 0)
    history["failures"] = int(history.get("failures", 0) or 0)

    if event.get("outcome") == "failure":
        history["failures"] += 1
    elif event.get("outcome") == "success":
        history["successes"] += 1

    _safe_write(EXECUTION_LOG, memory)
    _safe_write(IDENTITY_PATH, identity)

    return {"status": "recorded", "event": event}"""

if old in code:
    code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("EXECUTION_MEMORY_HISTORY_PATCHED")
