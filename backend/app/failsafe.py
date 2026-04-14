from fastapi import APIRouter, Request
from pathlib import Path
from datetime import datetime, timezone
import json, traceback, uuid

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
LOG_DIR = DATA_DIR / "failsafe"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"

LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ERROR_FILE = LOG_DIR / "errors.json"
RECOVERY_FILE = LOG_DIR / "recovery.json"

def _now():
    return datetime.now(timezone.utc).isoformat()

def _read_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except:
        pass
    return default

def _write_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _log_error(error, context):
    data = _read_json(ERROR_FILE, {"errors": []})
    entry = {
        "id": str(uuid.uuid4()),
        "time": _now(),
        "error": str(error),
        "trace": traceback.format_exc(),
        "context": context
    }
    data["errors"].append(entry)
    data["errors"] = data["errors"][-300:]
    _write_json(ERROR_FILE, data)
    return entry

def _log_recovery(action):
    data = _read_json(RECOVERY_FILE, {"events": []})
    event = {
        "time": _now(),
        "action": action
    }
    data["events"].append(event)
    data["events"] = data["events"][-300:]
    _write_json(RECOVERY_FILE, data)

def safe_execute(fn, context=None):
    try:
        result = fn()
        _log_recovery("success")
        return {
            "status": "ok",
            "result": result
        }
    except Exception as e:
        err = _log_error(e, context or {})
        _log_recovery("fallback_triggered")
        return {
            "status": "recovered",
            "error": str(e),
            "fallback": True,
            "error_id": err["id"],
            "result": {
                "message": "system recovered from failure",
                "context": context
            }
        }

@router.get("/api/failsafe/status")
def failsafe_status():
    errors = _read_json(ERROR_FILE, {}).get("errors", [])
    recovery = _read_json(RECOVERY_FILE, {}).get("events", [])

    return {
        "status": "ok",
        "phase": "failsafe immortality layer",
        "counts": {
            "errors": len(errors),
            "recoveries": len(recovery)
        },
        "recent_errors": errors[-10:],
        "recent_recovery_events": recovery[-10:]
    }

@router.post("/api/failsafe/test")
def failsafe_test():
    def crash():
        raise Exception("intentional test failure")

    return safe_execute(crash, {"test": True})

@router.post("/api/failsafe/wrap")
async def failsafe_wrap(request: Request):
    data = await request.json()
    action = data.get("action", "unknown")

    def simulated():
        if action == "fail":
            raise Exception("forced failure")
        return {"message": "executed safely", "action": action}

    return safe_execute(simulated, {"action": action})

