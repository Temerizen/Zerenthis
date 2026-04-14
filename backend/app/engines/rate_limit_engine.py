import time

LAST_CALL = 0
MIN_DELAY = 5

def throttle():
    global LAST_CALL
    now = time.time()
    if now - LAST_CALL < MIN_DELAY:
        time.sleep(MIN_DELAY - (now - LAST_CALL))
    LAST_CALL = time.time()

