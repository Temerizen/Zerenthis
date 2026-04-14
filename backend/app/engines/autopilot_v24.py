from __future__ import annotations
import time, threading, requests
from typing import List

BASE = "http://127.0.0.1:8000"

LOOPS = {
    "money": [
        "/api/revenue/intelligence",
        "/api/mutation/run",
        "/api/decision/real"
    ],
    "traffic": [
        "/api/promote/run",
        "/api/flood/run",
        "/api/deploy/live"
    ],
    "intelligence": [
        "/api/demand/intelligence/run",
        "/api/signals/auto-capture"
    ],
    "experiment": [
        "/api/swarm/real",
        "/api/self-improve/run"
    ]
}

def run_loop(name: str, endpoints: List[str], delay: float = 5.0):
    print(f"[START] {name}")
    cycle = 0
    while True:
        cycle += 1
        for ep in endpoints:
            try:
                r = requests.post(BASE + ep, timeout=10)
                print(f"[{name}] {ep} -> {r.status_code}")
            except Exception as e:
                print(f"[{name}] ERROR {ep}: {e}")
        time.sleep(delay)

def start_all():
    threads = []
    for name, eps in LOOPS.items():
        t = threading.Thread(target=run_loop, args=(name, eps), daemon=True)
        t.start()
        threads.append(t)

    while True:
        time.sleep(60)

if __name__ == "__main__":
    start_all()
