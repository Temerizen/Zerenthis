import threading
import time
import requests
import random
from fastapi import FastAPI

BASE = "https://semantiqai-backend-production-bcab.up.railway.app"

app = FastAPI(title="Zerenthis Autopilot v4")

MODULES = [
    "Money Engine",
    "Content Factory",
    "Video Engine",
    "AI School",
    "Research Engine",
    "Cognitive Lab"
]

def evolve():
    # 🔥 delay startup so API becomes healthy first
    time.sleep(10)

    while True:
        try:
            module = random.choice(MODULES)

            payload = {
                "topic": f"{module} automated system",
                "niche": "AI Automation",
                "tone": "Premium",
                "buyer": "Entrepreneurs",
                "promise": "generate results faster",
                "bonus": "templates + systems",
                "notes": f"autopilot evolution loop: {module}"
            }

            print(f"Running evolution for: {module}", flush=True)

            r = requests.post(f"{BASE}/api/product-pack", json=payload, timeout=20)
            data = r.json()

            job_id = data.get("job_id")
            file_url = data.get("file_url", "")
            file_name = file_url.split("/")[-1] if file_url else ""

            winner = {
                "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "module": module,
                "job_id": job_id or "",
                "score": 100,
                "file_url": file_url,
                "file_name": file_name,
                "payload": payload,
                "result": {}
            }

            requests.post(f"{BASE}/api/winners", json=winner, timeout=15)

            print(f"Winner pushed: {file_name}", flush=True)

            time.sleep(30)

        except Exception as e:
            print(f"Loop error: {e}", flush=True)
            time.sleep(10)

def start_background():
    thread = threading.Thread(target=evolve, daemon=True)
    thread.start()

# 🔥 CRITICAL: start thread WITHOUT blocking startup
start_background()

@app.get("/")
def root():
    return {"ok": True, "mode": "AUTOPILOT ACTIVE"}

@app.get("/health")
def health():
    return {"ok": True, "status": "running"}
