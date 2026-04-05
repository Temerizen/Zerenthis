import threading
from backend.app.core.core_loop import run_core_loop

_loop_started = False

def start_core_loop_once():
    global _loop_started
    if _loop_started:
        print("[CORE] loop already started, skipping duplicate", flush=True)
        return

    _loop_started = True
    print("[CORE] launching core loop (single instance)", flush=True)

    thread = threading.Thread(
        target=run_core_loop,
        daemon=True,
        name="zerenthis-core-loop"
    )
    thread.start()
