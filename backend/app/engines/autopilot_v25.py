from __future__ import annotations
import time, threading, requests, json, os
from typing import List

BASE = "http://127.0.0.1:8000"
PRIORITY_PATH = "backend/data/priority_state.json"

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

def get_priority():
    if not os.path.exists(PRIORITY_PATH):
        return list(LOOPS.keys())
    with open(PRIORITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("priority_order", list(LOOPS.keys()))

def run_loop(name: str, endpoints: List[str]):
    print(f"[START] {name}")
    while True:
        priority = get_priority()

        if name != priority[0]:
            time.sleep(6)  # slower if not top priority
            continue

        for ep in endpoints:
            try:
                r = requests.post(BASE + ep, timeout=10)
                print(f"[{name}] {ep} -> {r.status_code}")
            except Exception as e:
                print(f"[{name}] ERROR {ep}: {e}")

        time.sleep(2)  # faster if top loop

def run_priority_engine():
    while True:
        try:
            requests.post(BASE + "/api/priority/build")
        except:
            pass
        time.sleep(10)

def start_all():
    threads = []

    # start priority engine
    t_priority = threading.Thread(target=run_priority_engine, daemon=True)
    t_priority.start()

    for name, eps in LOOPS.items():
        t = threading.Thread(target=run_loop, args=(name, eps), daemon=True)
        t.start()
        threads.append(t)

    while True:
        time.sleep(60)

if __name__ == "__main__":
    start_all()
