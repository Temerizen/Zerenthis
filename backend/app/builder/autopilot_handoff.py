from __future__ import annotations
from backend.app.builder.autopilot_request_engine import build_request_from_autopilot

def execute_autopilot_builder_handoff(run_controller):
    envelope = build_request_from_autopilot()

    if envelope.get("status") != "builder_requested":
        return {
            "status": "no_builder_action",
            "signal": envelope.get("signal", {})
        }

    builder_request = envelope.get("builder_request", {})
    run_result = run_controller(builder_request)

    return {
        "status": "builder_handoff_executed",
        "signal": envelope.get("signal", {}),
        "builder_request": builder_request,
        "run_result": run_result
    }

