import os
import time, requests, os

BASE = os.getenv("PUBLIC_BASE_URL") or "http://semantiqai-backend.railway.internal:8080"

def run_cycle():
    print("=== AUTOPILOT CYCLE START ===")

    # 1. generate proposals
    props = requests.post(f"{BASE}/api/self-improver/run").json().get("proposals", [])

    if not props:
        print("No proposals")
        return

    # 2. pick top proposal
    top = sorted(props, key=lambda x: x.get("priority",0), reverse=True)[0]
    pid = top["id"]

    print("Top proposal:", top["title"])

    # 3. auto-approve
    requests.post(f"{BASE}/api/self-improver/approve", json={"id": pid})

    # 4. execute
    result = requests.post(f"{BASE}/api/self-improver/execute", json={"id": pid}).json()
    print("Execution:", result)

    # 5. run body loop using proposal topic
    topic = top["title"]

    body = requests.post(f"{BASE}/api/body-loop/run", json={
        "topic": topic,
        "buyer": "Founders",
        "promise": "grow faster",
        "niche": "Content Monetization",
        "tone": "Premium",
        "bonus": "templates",
        "notes": "autopilot run"
    }).json()

    manifest = body.get("manifest", {})
    script = manifest.get("content", {}).get("script", "")
    variants = manifest.get("variants", [])

    print("Generated content")

    # 6. build distribution pack
    dist = requests.post(f"{BASE}/api/distribution/build", json={
        "topic": topic,
        "buyer": "Founders",
        "promise": "grow faster",
        "niche": "Content Monetization",
        "script": script,
        "variants": variants
    }).json()

    # 7. enqueue top post
    if dist.get("tiktok"):
        post = dist["tiktok"][0]
        requests.post(f"{BASE}/api/distribution/queue", json={
            "platform": "tiktok",
            "content": post,
            "topic": topic
        })

    print("Queued content")
    print("=== AUTOPILOT CYCLE END ===\n")

if __name__ == "__main__":
    while True:
        try:
            run_cycle()
        except Exception as e:
            print("Error:", e)
        time.sleep(300)  # runs every 5 minutes





