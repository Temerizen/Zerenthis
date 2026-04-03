from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import os, json, threading, time

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AUTO_FILE = DATA_DIR / "autopilot_state.json"
APPROVALS_FILE = DATA_DIR / "approvals.json"
AUTO_LOG = DATA_DIR / "autopilot_runs.json"

DEFAULT_STATE = {
    "enabled": False,
    "mode": "safe",
    "interval_seconds": 900,
    "last_run_at": "",
    "last_result": "",
    "pending_approval": False,
    "approved_actions": []
}

_LOOP = {"thread": None, "stop": False}

def _now():
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_state():
    state = _read_json(AUTO_FILE, DEFAULT_STATE.copy())
    if not isinstance(state, dict):
        state = DEFAULT_STATE.copy()
    for k, v in DEFAULT_STATE.items():
        state.setdefault(k, v)
    return state

def save_state(state: dict):
    _write_json(AUTO_FILE, state)

def append_run(entry: dict):
    data = _read_json(AUTO_LOG, [])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    data = data[-200:]
    _write_json(AUTO_LOG, data)

def approvals():
    data = _read_json(APPROVALS_FILE, {"pending": [], "history": []})
    if not isinstance(data, dict):
        data = {"pending": [], "history": []}
    data.setdefault("pending", [])
    data.setdefault("history", [])
    return data

def save_approvals(data: dict):
    _write_json(APPROVALS_FILE, data)

def risk_level(action: dict) -> str:
    route = (action.get("route") or "").lower()
    kind = (action.get("kind") or "").lower()
    topic = (action.get("topic") or "").lower()

    if any(x in route for x in ["/delete", "/remove", "/wipe"]):
        return "high"
    if any(x in kind for x in ["delete", "destructive", "rewrite"]):
        return "high"
    if any(x in topic for x in ["adult", "gambling", "weapon", "drug"]):
        return "high"
    if any(x in route for x in ["/api/founder/run-winner-cycle", "/api/founder/full-stack-generate", "/api/monetize/package"]):
        return "low"
    return "medium"

def queue_approval(action: dict, reason: str):
    data = approvals()
    item = {
        "id": f"approval_{int(time.time()*1000)}",
        "created_at": _now(),
        "reason": reason,
        "action": action,
        "risk": risk_level(action),
        "status": "pending"
    }
    data["pending"].append(item)
    data["pending"] = data["pending"][-100:]
    data["history"] = data["history"][-300:]
    save_approvals(data)

    state = load_state()
    state["pending_approval"] = True
    save_state(state)
    return item

def approve_item(item_id: str):
    data = approvals()
    pending = data.get("pending", [])
    item = next((x for x in pending if x.get("id") == item_id), None)
    if not item:
        return None
    item["status"] = "approved"
    item["approved_at"] = _now()
    data["pending"] = [x for x in pending if x.get("id") != item_id]
    data["history"].append(item)
    save_approvals(data)

    state = load_state()
    state["pending_approval"] = len(data["pending"]) > 0
    state["approved_actions"] = (state.get("approved_actions", []) + [item_id])[-100:]
    save_state(state)
    return item

def reject_item(item_id: str):
    data = approvals()
    pending = data.get("pending", [])
    item = next((x for x in pending if x.get("id") == item_id), None)
    if not item:
        return None
    item["status"] = "rejected"
    item["rejected_at"] = _now()
    data["pending"] = [x for x in pending if x.get("id") != item_id]
    data["history"].append(item)
    save_approvals(data)

    state = load_state()
    state["pending_approval"] = len(data["pending"]) > 0
    save_state(state)
    return item

def _safe_run_cycle(topic: str):
    result = {
        "time": _now(),
        "topic": topic,
        "steps": [],
        "status": "ok"
    }

    try:
        from backend.app.winner_cycle import run_winner_cycle
        winner = run_winner_cycle({
            "topic": topic,
            "notes": "autopilot safe winner cycle"
        })
        result["steps"].append({"step": "winner_cycle", "result": winner})
    except Exception as e:
        result["steps"].append({"step": "winner_cycle", "error": str(e)})

    try:
        from backend.app.monetization import monetize_package
        monetized = monetize_package({
            "topic": topic,
            "notes": "autopilot safe monetize"
        })
        result["steps"].append({"step": "monetize_package", "result": monetized})
    except Exception as e:
        result["steps"].append({"step": "monetize_package", "error": str(e)})

    return result

def _aggressive_run_cycle(topic: str):
    result = _safe_run_cycle(topic)

    try:
        from backend.app.intelligence import intel_evolve
        intel = intel_evolve({
            "topic": topic,
            "notes": "autopilot aggressive evolve"
        })
        result["steps"].append({"step": "intel_evolve", "result": intel})
    except Exception as e:
        result["steps"].append({"step": "intel_evolve", "error": str(e)})

    return result

def execute_action(action: dict):
    topic = action.get("topic", "Faceless TikTok AI starter pack for beginners")
    mode = action.get("mode", "safe")
    risk = risk_level(action)

    if risk == "high":
        approval = queue_approval(action, "High-risk action requires founder approval")
        return {
            "status": "queued_for_approval",
            "approval": approval
        }

    if risk == "medium" and mode != "safe":
        approval = queue_approval(action, "Medium-risk non-safe action requires founder approval")
        return {
            "status": "queued_for_approval",
            "approval": approval
        }

    if mode == "aggressive":
        run = _aggressive_run_cycle(topic)
    else:
        run = _safe_run_cycle(topic)

    append_run(run)

    state = load_state()
    state["last_run_at"] = _now()
    state["last_result"] = "ok"
    save_state(state)

    return {
        "status": "executed",
        "mode": mode,
        "risk": risk,
        "run": run
    }

def autopilot_loop():
    while not _LOOP["stop"]:
        state = load_state()
        if state.get("enabled"):
            topic = "Faceless TikTok AI starter pack for beginners"
            try:
                outcome = execute_action({
                    "kind": "autopilot_cycle",
                    "route": "/api/autopilot/tick",
                    "topic": topic,
                    "mode": state.get("mode", "safe")
                })
                state["last_run_at"] = _now()
                state["last_result"] = outcome.get("status", "unknown")
                save_state(state)
            except Exception as e:
                state["last_run_at"] = _now()
                state["last_result"] = f"error: {str(e)}"
                save_state(state)
        sleep_for = max(int(state.get("interval_seconds", 900)), 60)
        for _ in range(sleep_for):
            if _LOOP["stop"]:
                break
            time.sleep(1)

def ensure_loop():
    if _LOOP["thread"] and _LOOP["thread"].is_alive():
        return
    _LOOP["stop"] = False
    t = threading.Thread(target=autopilot_loop, daemon=True)
    _LOOP["thread"] = t
    t.start()

@router.get("/api/autopilot/status")
def autopilot_status():
    state = load_state()
    appr = approvals()
    runs = _read_json(AUTO_LOG, [])
    return {
        "status": "ok",
        "phase": "true autopilot",
        "autopilot": state,
        "pending_approvals": appr.get("pending", []),
        "recent_runs": (runs[-10:] if isinstance(runs, list) else [])
    }

@router.post("/api/autopilot/configure")
def autopilot_configure(payload: dict = Body(...)):
    state = load_state()
    mode = str(payload.get("mode", state.get("mode", "safe"))).lower()
    if mode not in ("safe", "aggressive"):
        mode = "safe"

    interval_seconds = int(payload.get("interval_seconds", state.get("interval_seconds", 900)))
    interval_seconds = max(60, interval_seconds)

    state["mode"] = mode
    state["interval_seconds"] = interval_seconds
    if "enabled" in payload:
        state["enabled"] = bool(payload.get("enabled"))
    save_state(state)
    ensure_loop()

    return {
        "status": "ok",
        "autopilot": state
    }

@router.post("/api/autopilot/start")
def autopilot_start(payload: dict = Body(default={})):
    state = load_state()
    state["enabled"] = True
    if payload.get("mode") in ("safe", "aggressive"):
        state["mode"] = payload.get("mode")
    if payload.get("interval_seconds"):
        state["interval_seconds"] = max(60, int(payload.get("interval_seconds")))
    save_state(state)
    ensure_loop()
    return {
        "status": "ok",
        "message": "autopilot started",
        "autopilot": state
    }

@router.post("/api/autopilot/stop")
def autopilot_stop():
    state = load_state()
    state["enabled"] = False
    save_state(state)
    return {
        "status": "ok",
        "message": "autopilot stopped",
        "autopilot": state
    }

@router.post("/api/autopilot/tick")
def autopilot_tick(payload: dict = Body(default={})):
    mode = payload.get("mode", load_state().get("mode", "safe"))
    topic = payload.get("topic", "Faceless TikTok AI starter pack for beginners")
    action = {
        "kind": payload.get("kind", "manual_tick"),
        "route": "/api/autopilot/tick",
        "topic": topic,
        "mode": mode
    }
    return execute_action(action)

@router.get("/api/autopilot/approvals")
def autopilot_approvals():
    return {
        "status": "ok",
        "approvals": approvals()
    }

@router.post("/api/autopilot/approve")
def autopilot_approve(payload: dict = Body(...)):
    item_id = payload.get("id", "")
    item = approve_item(item_id)
    if not item:
        return {"status": "error", "error": "approval not found"}

    action = item.get("action", {})
    action["mode"] = action.get("mode", "aggressive")
    outcome = execute_action(action)

    return {
        "status": "ok",
        "approved": item,
        "outcome": outcome
    }

@router.post("/api/autopilot/reject")
def autopilot_reject(payload: dict = Body(...)):
    item_id = payload.get("id", "")
    item = reject_item(item_id)
    if not item:
        return {"status": "error", "error": "approval not found"}
    return {
        "status": "ok",
        "rejected": item
    }

ensure_loop()
