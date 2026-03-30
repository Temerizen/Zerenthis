from __future__ import annotations

import time
from backend.empire.engine import bootstrap, run_cycle

def run():
    bootstrap()
    print("Empire intelligence loop started.")
    while True:
        result = run_cycle()
        print("Empire reflection:", result["operator_judgment"])
        time.sleep(120)

if __name__ == "__main__":
    run()
