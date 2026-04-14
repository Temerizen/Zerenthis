import hashlib
import hmac
from flask import request
from backend.core.config import FOUNDER_KEY, FOUNDER_MODE

def founder_access_granted() -> bool:
    if not FOUNDER_MODE:
        return False

    expected = (FOUNDER_KEY or "").strip()
    if not expected:
        return False

    provided = (
        request.headers.get("X-Founder-Key", "") or
        request.args.get("founder_key", "") or
        ((request.get_json(silent=True) or {}).get("founder_key", ""))
    ).strip()

    if not provided:
        return False

    return hmac.compare_digest(
        hashlib.sha256(provided.encode()).hexdigest(),
        hashlib.sha256(expected.encode()).hexdigest()
    )

