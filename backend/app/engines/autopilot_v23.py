from __future__ import annotations
import time, json, os
from typing import Dict, Any
import requests

BASE = "http://127.0.0.1:8000"
STATE_PATH = "backend/data/autopilot_v23_state.json"

ENDPOINTS = [
    "/api/revenue/intelligence",
    "/api/swarm/real",
    "/api/promote/run",
    "/api/flood/run",
    "/api/deploy/live"
]

def _save(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def _run_cycle(cycle: int):
    results = []

    for ep in ENDPOINTS:
        try:
            r = requests.post(BASE + ep, timeout=20)
            results.append({
                "endpoint": ep,
                "status": r.status_code
            })
        except Exception as e:
            results.append({
                "endpoint": ep,
                "status": "error",
                "error": str(e)
            })

    return results

def run_autopilot_v23(max_cycles: int = 999999, base_delay: float = 10.0) -> Dict[str, Any]:
    history = []
    delay = base_delay

    for i in range(max_cycles):
        cycle_num = i + 1

        results = _run_cycle(cycle_num)

        # simple adaptive logic
        success_count = sum(1 for r in results if r.get("status") == 200)

        if success_count >= len(results) - 1:
            delay = max(5, delay * 0.9)  # speed up
        else:
            delay = min(60, delay * 1.2)  # slow down if errors

        state = {
            "status": "running",
            "cycle": cycle_num,
            "delay": delay,
            "results": results,
            "timestamp": time.time()
        }

        history.append(state)
        _save({
            "current": state,
            "recent": history[-5:]
        })

        time.sleep(delay)

    return {
        "status": "completed",
        "cycles": max_cycles
    }
