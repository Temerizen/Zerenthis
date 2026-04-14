from __future__ import annotations
import time, json, os, threading
from typing import Dict, Any
import requests

BASE = "http://127.0.0.1:8000"
STATE_PATH = "backend/data/autopilot_state.json"

ENDPOINTS = [
    "/api/revenue/intelligence",
    "/api/mutation/run",
    "/api/strategic-memory/run",
    "/api/traffic/intelligence/run",
    "/api/scaling/run",
    "/api/self-improve/run",
    "/api/demand/intelligence/run",
    "/api/decision/real",
    "/api/promotion/run",
    "/api/signals/auto-capture",
    "/api/decision/real"
]

_AUTOPILOT_LOCK = threading.Lock()
_AUTOPILOT_RUNNING = False

def _load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_state(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _run_cycle(cycle: int) -> Dict[str, Any]:
    results = []
    for ep in ENDPOINTS:
        try:
            r = requests.post(BASE + ep, timeout=15)
            results.append({"endpoint": ep, "status": r.status_code})
        except Exception as e:
            results.append({"endpoint": ep, "status": "error", "error": str(e)})
    return {
        "cycle": cycle,
        "results": results,
        "timestamp": time.time()
    }

def _autopilot_worker(max_cycles: int, delay: float) -> None:
    global _AUTOPILOT_RUNNING
    history = []

    try:
        _save_state({
            "status": "running",
            "current_cycle": 0,
            "max_cycles": max_cycles,
            "delay": delay,
            "history_tail": [],
            "timestamp": time.time()
        })

        for i in range(max_cycles):
            cycle_data = _run_cycle(i + 1)
            history.append(cycle_data)

            _save_state({
                "status": "running",
                "current_cycle": i + 1,
                "max_cycles": max_cycles,
                "delay": delay,
                "history_tail": history[-5:],
                "timestamp": time.time()
            })

            time.sleep(delay)

        _save_state({
            "status": "completed",
            "current_cycle": max_cycles,
            "max_cycles": max_cycles,
            "delay": delay,
            "history_tail": history[-5:],
            "timestamp": time.time()
        })
    except Exception as e:
        _save_state({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        })
    finally:
        with _AUTOPILOT_LOCK:
            _AUTOPILOT_RUNNING = False

def start_autopilot(max_cycles: int = 10, delay: float = 2.0) -> Dict[str, Any]:
    global _AUTOPILOT_RUNNING
    with _AUTOPILOT_LOCK:
        if _AUTOPILOT_RUNNING:
            return {
                "status": "already_running",
                "state": _load_state()
            }

        _AUTOPILOT_RUNNING = True
        thread = threading.Thread(
            target=_autopilot_worker,
            args=(max_cycles, delay),
            daemon=True
        )
        thread.start()

    return {
        "status": "started",
        "max_cycles": max_cycles,
        "delay": delay
    }

def get_autopilot_status() -> Dict[str, Any]:
    state = _load_state()
    if not state:
        return {"status": "idle"}
    return state
