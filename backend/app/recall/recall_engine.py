import time
from backend.app.recall.memory_store import add

def loop():
    i = 0
    while True:
        add({
            "type": "system_progress",
            "content": f"Cycle {i}: Zerenthis is evolving"
        })
        i += 1
        time.sleep(3)