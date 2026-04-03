import os
import json
import time
from threading import Lock
from fastapi import APIRouter, Request, HTTPException

DATA_DIR = "backend/data"
STATE_FILE = os.path.join(DATA_DIR, "limits_state.json")
os.makedirs(DATA_DIR, exist_ok=True)

_router = APIRouter()
_lock = Lock()

LIMITS = {
    "window_seconds": 60,
    "max_requests_per_window": 30,
    "max_generation_requests_per_window": 8,
    "max_payload_chars": 12000,
    "daily_generation_cap": 60
}

def _today():
    return time.strftime("%Y-%m-%d")

def _load():
    if not os.path.exists(STATE_FILE):
        return {"ips": {}, "daily": {}}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"ips": {}, "daily": {}}

def _save(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for", "").strip()
    if xff:
        return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"

def founder_bypass(request: Request) -> bool:
    env_key = os.getenv("FOUNDER_KEY", "").strip()
    hdr_key = request.headers.get("x-founder-key", "").strip()
    return bool(env_key and hdr_key and env_key == hdr_key)

def enforce_payload_limit(payload):
    if payload is None:
        return
    raw = json.dumps(payload, ensure_ascii=False)
    if len(raw) > LIMITS["max_payload_chars"]:
        raise HTTPException(status_code=413, detail=f"Payload too large. Max {LIMITS['max_payload_chars']} characters.")

def enforce_rate_limit(request: Request, route_type: str = "general"):
    if founder_bypass(request):
        return {"ok": True, "founder_bypass": True, "ip": client_ip(request)}

    ip = client_ip(request)
    now = time.time()

    with _lock:
        state = _load()
        ips = state.setdefault("ips", {})
        entry = ips.setdefault(ip, {
            "window_start": now,
            "requests": 0,
            "generation_requests": 0,
            "last_seen": now
        })

        if now - entry["window_start"] > LIMITS["window_seconds"]:
            entry["window_start"] = now
            entry["requests"] = 0
            entry["generation_requests"] = 0

        entry["requests"] += 1
        entry["last_seen"] = now

        if entry["requests"] > LIMITS["max_requests_per_window"]:
            _save(state)
            raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

        if route_type == "generation":
            entry["generation_requests"] += 1
            if entry["generation_requests"] > LIMITS["max_generation_requests_per_window"]:
                _save(state)
                raise HTTPException(status_code=429, detail="Generation limit hit. Wait a minute and try again.")

            today = _today()
            daily = state.setdefault("daily", {})
            day_bucket = daily.setdefault(today, {})
            day_bucket[ip] = day_bucket.get(ip, 0) + 1

            if day_bucket[ip] > LIMITS["daily_generation_cap"]:
                _save(state)
                raise HTTPException(status_code=429, detail="Daily generation cap reached for this IP.")

        _save(state)

    return {"ok": True, "founder_bypass": False, "ip": ip}

def get_limit_stats():
    state = _load()
    today = _today()
    return {
        "ok": True,
        "limits": LIMITS,
        "today": today,
        "daily_counts": state.get("daily", {}).get(today, {}),
        "tracked_ips": len(state.get("ips", {}))
    }

@_router.get("/api/limits/stats")
def limits_stats():
    return get_limit_stats()

router = _router
