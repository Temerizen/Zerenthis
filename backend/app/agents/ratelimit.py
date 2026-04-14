import time

_BUCKETS = {}

def allow(key: str, limit: int = 30, window_seconds: int = 60):
    now = time.time()
    bucket = _BUCKETS.get(key, [])
    bucket = [t for t in bucket if now - t < window_seconds]
    if len(bucket) >= limit:
        _BUCKETS[key] = bucket
        return False, max(1, int(window_seconds - (now - bucket[0])))
    bucket.append(now)
    _BUCKETS[key] = bucket
    return True, 0


