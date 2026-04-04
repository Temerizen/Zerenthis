from time import time

RATE_LIMIT = {}
LIMIT = 60  # requests
WINDOW = 60  # seconds

def is_limited(ip):
    now = time()

    if ip not in RATE_LIMIT:
        RATE_LIMIT[ip] = []

    RATE_LIMIT[ip] = [t for t in RATE_LIMIT[ip] if now - t < WINDOW]

    if len(RATE_LIMIT[ip]) >= LIMIT:
        return True

    RATE_LIMIT[ip].append(now)
    return False
