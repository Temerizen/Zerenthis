import json
import os
import threading
import time
from datetime import datetime, timezone

STATE_PATH = os.path.join("backend", "data", "core_loop_state.json")
_LOOP_LOCK = threading.Lock()

def _utc_now():
    return datetime.now(timezone.utc).isoformat()

def _log(message: str):
    print(message, flush=True)

def _write_state(state: dict):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def safe_import():
    try:
        from backend.app.engines.builder_engine import run_builder
    except Exception:
        run_builder = lambda cid: None

    try:
        from backend.app.engines.execution_engine import run_execution
    except Exception:
        run_execution = lambda cid: None

    try:
        from backend.app.engines.money_engine import run_money
    except Exception:
        run_money = lambda cid: None

    try:
        from backend.app.engines.self_improver import run_self_improver
    except Exception:
        run_self_improver = lambda cid: None

    return run_builder, run_execution, run_money, run_self_improver

def _run_stage(label, cid, fn):
    _log(f"[{label}][{cid}] START")
    fn(cid)
    _log(f"[{label}][{cid}] DONE")

def run_core_loop():
    run_builder, run_execution, run_money, run_self_improver = safe_import()
    cycle = 0

    while True:
        cycle += 1
        cid = f"CYCLE-{cycle}"

        if not _LOOP_LOCK.acquire(blocking=False):
            _log(f"[CORE][{cid}] SKIP_LOCK_ACTIVE")
            time.sleep(5)
            continue

        started_at = _utc_now()

        try:
            _log(f"[CORE][{cid}] START")

            _write_state({
                "status": "running",
                "cycle": cycle,
                "started_at": started_at,
                "finished_at": None,
                "last_error": None
            })

            _run_stage("BUILDER", cid, run_builder)
            _run_stage("EXECUTION", cid, run_execution)
            _run_stage("MONEY", cid, run_money)
            _run_stage("SELF", cid, run_self_improver)

            finished_at = _utc_now()

            _write_state({
                "status": "idle",
                "cycle": cycle,
                "started_at": started_at,
                "finished_at": finished_at,
                "last_error": None
            })

            _log(f"[CORE][{cid}] COMPLETE")

        except Exception as e:
            _write_state({
                "status": "error",
                "cycle": cycle,
                "started_at": started_at,
                "finished_at": None,
                "last_error": str(e)
            })
            _log(f"[CORE][{cid}] ERROR: {str(e)}")

        finally:
            _LOOP_LOCK.release()

        time.sleep(30)

