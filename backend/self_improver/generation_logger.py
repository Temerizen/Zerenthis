from datetime import datetime
from self_improver.outcome_engine import log_result

def log_generation_event(kind: str, payload: dict, status: str = "generated", extra: dict | None = None):
    entry = {
        "event": "generation",
        "kind": kind,
        "status": status,
        "topic": payload.get("topic"),
        "niche": payload.get("niche"),
        "tone": payload.get("tone"),
        "buyer": payload.get("buyer"),
        "promise": payload.get("promise"),
        "bonus": payload.get("bonus"),
        "notes": payload.get("notes"),
        "duration_seconds": payload.get("duration_seconds"),
        "count": payload.get("count"),
        "score": 0,
        "views": 0,
        "clicks": 0,
        "sales": 0,
        "timestamp": str(datetime.utcnow()),
    }
    if extra:
        entry.update(extra)
    return log_result(entry)
