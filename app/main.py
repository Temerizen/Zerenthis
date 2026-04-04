import threading
import time
import requests
import random

BASE = "https://semantiqai-backend-production-bcab.up.railway.app"

MODULES = [
    "Money Engine",
    "Content Factory",
    "Video Engine",
    "AI School",
    "Research Engine",
    "Cognitive Lab"
]

def evolve():
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

            print(f"🚀 Running evolution for: {module}")

            r = requests.post(f"{BASE}/api/product-pack", json=payload, timeout=60)
            data = r.json()

            job_id = data.get("job_id")
            file_url = data.get("file_url")

            winner = {
                "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "module": module,
                "job_id": job_id,
                "score": 100,
                "file_url": file_url,
                "file_name": file_url.split("/")[-1] if file_url else "",
                "payload": payload,
                "result": {}
            }

            requests.post(f"{BASE}/api/winners", json=winner, timeout=30)

            print(f"🏆 Winner pushed: {file_url}")

            time.sleep(25)

        except Exception as e:
            print("⚠️ Loop error:", e)
            time.sleep(10)

def start():
    threading.Thread(target=evolve, daemon=True).start()

start()

from fastapi import FastAPI

app = FastAPI(title="Zerenthis Autopilot v2")

@app.get("/")
def root():
    return {"ok": True, "mode": "AUTOPILOT ACTIVE"}

@app.get("/health")
def health():
    return {"ok": True, "status": "evolving"}
