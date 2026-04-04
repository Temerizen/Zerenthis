import os
import time, requests, os

BASE = os.getenv("PUBLIC_BASE_URL") or "http://semantiqai-backend.railway.internal:8080"

def analyze(history):
    if not history:
        return None

    # pick lowest scoring (needs fixing)
    worst = sorted(history, key=lambda x: x.get("scores",{}).get("overall",5))[0]
    return worst

def improve(target):
    topic = target.get("topic","")

    # surgical improvement logic
    return {
        "topic": f"How to master {topic} (optimized)",
        "buyer": target.get("buyer","Founders"),
        "promise": "get faster results with less effort",
        "niche": target.get("niche","Content Monetization"),
        "tone": "Premium",
        "bonus": "improved hooks + structure",
        "notes": "surgical improvement run"
    }

def run_cycle():
    print("=== SURGEON CYCLE START ===")

    # 1. observe
    history = requests.get(f"{BASE}/api/body-loop/history?limit=10").json().get("items",[])
    if not history:
        print("No history yet")
        return

    # 2. diagnose
    target = analyze(history)
    print("Target for improvement:", target.get("topic"))

    # 3. propose improvement
    improved_input = improve(target)

    # 4. act
    new_run = requests.post(f"{BASE}/api/body-loop/run", json=improved_input).json()

    manifest = new_run.get("manifest", {})
    new_score = manifest.get("scores",{}).get("overall",0)
    old_score = target.get("scores",{}).get("overall",0)

    print(f"Old score: {old_score} → New score: {new_score}")

    # 5. verify improvement
    if new_score > old_score:
        print("Improvement successful")

        # push to distribution
        script = manifest.get("content",{}).get("script","")
        variants = manifest.get("variants",[])

        dist = requests.post(f"{BASE}/api/distribution/build", json={
            "topic": improved_input["topic"],
            "buyer": improved_input["buyer"],
            "promise": improved_input["promise"],
            "niche": improved_input["niche"],
            "script": script,
            "variants": variants
        }).json()

        if dist.get("tiktok"):
            requests.post(f"{BASE}/api/distribution/queue", json={
                "platform":"tiktok",
                "content": dist["tiktok"][0],
                "topic": improved_input["topic"]
            })

        print("Queued improved content")

    else:
        print("No improvement, discarded")

    print("=== SURGEON CYCLE END ===\n")

if __name__ == "__main__":
    while True:
        try:
            run_cycle()
        except Exception as e:
            print("Error:", e)
        time.sleep(600)  # every 10 minutes





