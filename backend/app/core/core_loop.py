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
    except:
        run_builder = lambda cid: _log(f"[BUILDER][{cid}] skipped")

    try:
        from backend.app.engines.execution_engine import run_execution
    except:
        run_execution = lambda cid: _log(f"[EXECUTION][{cid}] skipped")

    try:
        from backend.app.engines.money_engine import run_money
    except:
        run_money = lambda cid: _log(f"[MONEY][{cid}] skipped")

    try:
        from backend.app.engines.self_improver import run_self_improver
    except:
        run_self_improver = lambda cid: _log(f"[SELF][{cid}] skipped")

    return run_builder, run_execution, run_money, run_self_improver

def run_core_loop():
    run_builder, run_execution, run_money, run_self_improver = safe_import()
    cycle = 0

    while True:
        cycle += 1
        cid = f"CYCLE-{cycle}"

        if not _LOOP_LOCK.acquire(blocking=False):
            _log(f"[CORE][{cid}] skipped (lock active)")
            time.sleep(5)
            continue

        started_at = _utc_now()

        try:
            _log(f"[CORE][{cid}] START")

            _write_state({
                "status": "running",
                "cycle": cycle,
                "started_at": started_at
            })

            run_builder(cid)
            run_execution(cid)
            run_money(cid)
            run_self_improver(cid)

            finished_at = _utc_now()

            _write_state({
                "status": "idle",
                "cycle": cycle,
                "started_at": started_at,
                "finished_at": finished_at
            })

            _log(f"[CORE][{cid}] COMPLETE")

        except Exception as e:
            _log(f"[CORE][{cid}] ERROR: {str(e)}")

        finally:
            _LOOP_LOCK.release()

        time.sleep(30)
