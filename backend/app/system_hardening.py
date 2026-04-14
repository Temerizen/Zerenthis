from fastapi import APIRouter
from datetime import datetime, timezone
from pathlib import Path
import os, json, traceback, time

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ERROR_LOG = LOG_DIR / "errors.jsonl"
EVENT_LOG = LOG_DIR / "events.jsonl"
HEALTH_LOG = LOG_DIR / "health.json"

def _now():
    return datetime.now(timezone.utc).isoformat()

def _append_jsonl(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

def log_event(kind: str, message: str, extra: dict | None = None):
    payload = {
        "time": _now(),
        "kind": kind,
        "message": message,
        "extra": extra or {}
    }
    _append_jsonl(EVENT_LOG, payload)
    return payload

def log_error(route: str, error: str, trace: str = "", extra: dict | None = None):
    payload = {
        "time": _now(),
        "route": route,
        "error": error,
        "trace": trace,
        "extra": extra or {}
    }
    _append_jsonl(ERROR_LOG, payload)
    return payload

def safe_retry(func, attempts=3, delay=0.6, route="system", *args, **kwargs):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            result = func(*args, **kwargs)
            log_event("retry_success", f"{route} succeeded", {"attempt": attempt})
            return {
                "status": "success",
                "attempt": attempt,
                "result": result
            }
        except Exception as e:
            last_error = e
            log_error(
                route=route,
                error=str(e),
                trace=traceback.format_exc(),
                extra={"attempt": attempt}
            )
            if attempt < attempts:
                time.sleep(delay)
    return {
        "status": "error",
        "attempts": attempts,
        "error": str(last_error) if last_error else "unknown error"
    }

def verify_outputs():
    files = []
    missing = []
    if OUTPUT_DIR.exists():
        for p in OUTPUT_DIR.iterdir():
            if p.is_file():
                try:
                    files.append({
                        "name": p.name,
                        "size": p.stat().st_size,
                        "modified_at": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
                    })
                except Exception:
                    pass
    else:
        missing.append("output_dir_missing")
    files.sort(key=lambda x: x["modified_at"], reverse=True)
    return {
        "output_dir_exists": OUTPUT_DIR.exists(),
        "output_count": len(files),
        "recent_outputs": files[:12],
        "missing": missing
    }

def write_health_snapshot():
    data = {
        "time": _now(),
        "paths": {
            "base_dir": str(BASE_DIR),
            "data_dir": str(DATA_DIR),
            "output_dir": str(OUTPUT_DIR),
            "log_dir": str(LOG_DIR)
        },
        "logs": {
            "event_log_exists": EVENT_LOG.exists(),
            "error_log_exists": ERROR_LOG.exists()
        },
        "outputs": verify_outputs()
    }
    with open(HEALTH_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return data

@router.get("/api/health/system")
def system_health():
    try:
        snapshot = write_health_snapshot()
        log_event("health_check", "system health check complete")
        return {
            "status": "ok",
            "phase": "system hardening",
            "health": snapshot
        }
    except Exception as e:
        log_error("/api/health/system", str(e), traceback.format_exc())
        return {
            "status": "error",
            "phase": "system hardening",
            "error": str(e)
        }

@router.get("/api/health/logs")
def health_logs():
    try:
        error_tail = []
        event_tail = []

        if ERROR_LOG.exists():
            with open(ERROR_LOG, "r", encoding="utf-8") as f:
                error_tail = [json.loads(line) for line in f.readlines()[-20:] if line.strip()]

        if EVENT_LOG.exists():
            with open(EVENT_LOG, "r", encoding="utf-8") as f:
                event_tail = [json.loads(line) for line in f.readlines()[-20:] if line.strip()]

        return {
            "status": "ok",
            "errors_recent": error_tail,
            "events_recent": event_tail
        }
    except Exception as e:
        log_error("/api/health/logs", str(e), traceback.format_exc())
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/api/health/verify-outputs")
def verify_outputs_route():
    try:
        result = verify_outputs()
        log_event("verify_outputs", "output verification complete", {"count": result.get("output_count", 0)})
        return {
            "status": "ok",
            "verification": result
        }
    except Exception as e:
        log_error("/api/health/verify-outputs", str(e), traceback.format_exc())
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/api/health/retry-smoke")
def retry_smoke():
    def _smoke():
        return {"message": "retry layer working", "time": _now()}
    return safe_retry(_smoke, attempts=3, delay=0.2, route="/api/health/retry-smoke")

