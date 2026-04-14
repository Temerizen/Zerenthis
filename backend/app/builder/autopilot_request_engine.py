from __future__ import annotations
from backend.app.builder.autopilot_bridge import detect_builder_need_with_queue

def build_request_from_autopilot() -> dict:
    signal = detect_builder_need_with_queue()

    if not signal.get("should_build"):
        return {
            "status": "no_builder_action",
            "signal": signal
        }

    target = signal.get("target")

    return {
        "status": "builder_requested",
        "signal": signal,
        "builder_request": {
            "type": "builder",
            "data": {
                "goal": "Improve weakest system component",
                "target": target,
                "reason": signal.get("reason"),
                "priority": signal.get("priority", "medium")
            }
        }
    }

