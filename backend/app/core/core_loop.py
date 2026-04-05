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
    print(f"[CORE {_utc_now()}] {message}", flush=True)

def _write_state(state: dict):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def safe_import():
    try:
        from backend.app.engines.builder_engine import run_builder
    except Exception as e:
        _log(f"builder import failed, using skip stub: {e}")
        run_builder = lambda: _log("builder skipped")

    try:
        from backend.app.engines.execution_engine import run_execution
    except Exception as e:
        _log(f"execution import failed, using skip stub: {e}")
        run_execution = lambda: _log("execution skipped")

    try:
        from backend.app.engines.money_engine import run_money
    except Exception as e:
        _log(f"money import failed, using skip stub: {e}")
        run_money = lambda: _log("money skipped")

    try:
        from backend.app.engines.self_improver import run_self_improver
    except Exception as e:
        _log(f"self improver import failed, using skip stub: {e}")
        run_self_improver = lambda: _log("self improver skipped")

    return run_builder, run_execution, run_money, run_self_improver

def run_core_loop():
    _log("Zerenthis Core Loop SAFE MODE started")
    run_builder, run_execution, run_money, run_self_improver = safe_import()
    cycle = 0

    while True:
        cycle += 1
        started_at = _utc_now()

        if not _LOOP_LOCK.acquire(blocking=False):
            _log("previous loop cycle still active, skipping overlap")
            time.sleep(5)
            continue

        try:
            _write_state({
                "status": "running",
                "cycle": cycle,
                "started_at": started_at,
                "last_completed_at": None,
                "last_error": None
            })

            _log(f"cycle {cycle} starting")
            run_builder()
            run_execution()
            run_money()
            run_self_improver()

            finished_at = _utc_now()
            _write_state({
                "status": "idle",
                "cycle": cycle,
                "started_at": started_at,
                "last_completed_at": finished_at,
                "last_error": None
            })
            _log(f"cycle {cycle} completed")
        except Exception as e:
            error_text = str(e)
            _write_state({
                "status": "error",
                "cycle": cycle,
                "started_at": started_at,
                "last_completed_at": None,
                "last_error": error_text
            })
            _log(f"cycle {cycle} error: {error_text}")
        finally:
            _LOOP_LOCK.release()

        time.sleep(30)
