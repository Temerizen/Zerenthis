import os
import threading
import time
import requests
import random

BASE_URL = os.getenv("BASE_URL") or os.getenv("PUBLIC_BASE_URL") or "http://zerenthis-main.railway.internal:8080"

TOPICS = [
    "Faceless TikTok automation system",
    "AI side hustle blueprint",
    "Digital product money machine",
    "Beginner content monetization system",
    "YouTube automation cash flow system"
]

def generate_payload():
    topic = random.choice(TOPICS)
    return {
        "topic": topic,
        "niche": "Content Monetization",
        "tone": "Premium",
        "buyer": "Beginners",
        "promise": "get results faster with less effort",
        "bonus": "templates, hooks, and shortcuts",
        "notes": "auto-evolution loop"
    }

def run_loop():
    print("🚀 Zerenthis Loop Started")

    while True:
        try:
            payload = generate_payload()

            print(f"\n⚡ Generating: {payload['topic']}")

            r = requests.post(f"{BASE_URL}/api/product-pack", json=payload, timeout=60)
            data = r.json()

            job_id = data.get("job_id")

            if not job_id:
                print("❌ No job_id returned")
                time.sleep(5)
                continue

            time.sleep(5)

            job = requests.get(f"{BASE_URL}/api/job/{job_id}").json()

            result = job.get("result", {})
            score = result.get("summary", {}).get("quality_score", 0)

            print(f"✅ Completed | Score: {score}")

            if score >= 90:
                print("🔥 HIGH QUALITY PRODUCT DETECTED")

            time.sleep(10)

        except Exception as e:
            print(f"⚠️ Loop error: {e}")
            time.sleep(10)

threading.Thread(target=run_loop, daemon=True).start()


