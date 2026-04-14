from __future__ import annotations
import json
import time
from pathlib import Path

from backend.app.builder.autopilot_request_engine import build_request_from_autopilot
from backend.app.builder.autopilot_bridge import detect_builder_need

LOOP_LOG = Path("backend/data/builder/continuous_loop_log.json")

def _load_log() -> list:
    if LOOP_LOG.exists():
        try:
            return json.loads(LOOP_LOG.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def _save_log(rows: list) -> None:
    LOOP_LOG.parent.mkdir(parents=True, exist_ok=True)
    LOOP_LOG.write_text(json.dumps(rows, indent=2), encoding="utf-8")

def run_continuous_builder_loop(run_controller, max_cycles: int = 5, delay_seconds: float = 1.0) -> dict:
    rows = _load_log()
    cycle_results = []
    consecutive_no_action = 0

    for cycle in range(1, max_cycles + 1):
        signal = detect_builder_need()
        envelope = build_request_from_autopilot()

        if envelope.get("status") != "builder_requested":
            consecutive_no_action += 1
            row = {
                "timestamp": int(time.time()),
                "cycle": cycle,
                "status": "no_builder_action",
                "signal": signal,
            }
            rows.append(row)
            cycle_results.append(row)

            if consecutive_no_action >= 2:
                break

            time.sleep(delay_seconds)
            continue

        consecutive_no_action = 0
        builder_request = envelope.get("builder_request", {})
        run_result = run_controller(builder_request)

        row = {
            "timestamp": int(time.time()),
            "cycle": cycle,
            "status": "builder_cycle_executed",
            "signal": signal,
            "builder_request": builder_request,
            "run_result": run_result,
        }
        rows.append(row)
        cycle_results.append(row)

        result_block = (((run_result or {}).get("result") or {}).get("apply_result") or {})
        if result_block.get("status") not in ("applied",):
            break

        time.sleep(delay_seconds)

    _save_log(rows)
    return {
        "status": "continuous_loop_complete",
        "cycles_run": len(cycle_results),
        "results": cycle_results,
    }

