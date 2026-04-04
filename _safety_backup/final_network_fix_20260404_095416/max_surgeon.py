import os
import time, requests, os, json, random
from datetime import datetime

BASE = os.getenv("PUBLIC_BASE_URL") or "http://zerenthis-main.railway.internal:8080"
MEMORY_PATH = "backend/data/surgeon_memory.json"

def _now():
    return datetime.utcnow().isoformat()+"Z"

def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return []
    try:
        return json.load(open(MEMORY_PATH,"r"))
    except:
        return []

def save_memory(data):
    json.dump(data, open(MEMORY_PATH,"w"), indent=2)

def weakest_dimension(scores):
    return min(["monetization","virality","clarity"], key=lambda k: scores.get(k,5))

def protocol(weakness):
    if weakness == "monetization":
        return {
            "promises": ["make money faster","turn this into income","high-converting system"],
            "bonuses": ["conversion templates","proven CTA stack","sales hooks"]
        }
    if weakness == "virality":
        return {
            "topics": ["secret method","mistakes nobody tells you","hack to explode growth"],
            "bonuses": ["scroll-stopping hooks","pattern interrupts"]
        }
    if weakness == "clarity":
        return {
            "notes": ["simplify steps","clear structure","step-by-step breakdown"]
        }
    return {}

def build_variants(base, weakness):
    p = protocol(weakness)
    variants = []

    for i in range(3):
        v = base.copy()

        if "promises" in p:
            v["promise"] = random.choice(p["promises"])
        if "topics" in p:
            v["topic"] = f"{base['topic']} - {random.choice(p['topics'])}"
        if "bonuses" in p:
            v["bonus"] = random.choice(p["bonuses"])
        if "notes" in p:
            v["notes"] = random.choice(p["notes"])

        variants.append(v)

    return variants

def already_failed(topic, weakness, memory):
    return any(m["topic"]==topic and m["weakness"]==weakness and m["result"]=="fail" for m in memory)

def run_cycle():
    print("=== MAX SURGEON CYCLE ===")

    memory = load_memory()

    history = requests.get(f"{BASE}/api/body-loop/history?limit=10").json().get("items",[])
    if not history:
        print("No history")
        return

    target = sorted(history, key=lambda x: x.get("scores",{}).get("overall",5))[0]
    topic = target.get("topic","")
    scores = target.get("scores",{})
    weakness = weakest_dimension(scores)

    print("Target:", topic)
    print("Weakness:", weakness)

    if already_failed(topic, weakness, memory):
        print("Skipping known failure pattern")
        return

    base_input = {
        "topic": topic,
        "buyer": target.get("buyer","Founders"),
        "promise": target.get("promise","grow faster"),
        "niche": target.get("niche","Content Monetization"),
        "tone": "Premium",
        "bonus": "optimized",
        "notes": "surgical run"
    }

    variants = build_variants(base_input, weakness)

    best_score = 0
    best_manifest = None

    for v in variants:
        res = requests.post(f"{BASE}/api/body-loop/run", json=v).json()
        manifest = res.get("manifest",{})
        score = manifest.get("scores",{}).get("overall",0)

        print("Variant score:", score)

        if score > best_score:
            best_score = score
            best_manifest = manifest

    old_score = scores.get("overall",0)

    if best_score > old_score:
        print(f"WINNER: {old_score} → {best_score}")

        script = best_manifest.get("content",{}).get("script","")
        variants_out = best_manifest.get("variants",[])

        dist = requests.post(f"{BASE}/api/distribution/build", json={
            "topic": best_manifest["input"]["topic"],
            "buyer": best_manifest["input"]["buyer"],
            "promise": best_manifest["input"]["promise"],
            "niche": best_manifest["input"]["niche"],
            "script": script,
            "variants": variants_out
        }).json()

        if dist.get("tiktok"):
            requests.post(f"{BASE}/api/distribution/queue", json={
                "platform":"tiktok",
                "content": dist["tiktok"][0],
                "topic": best_manifest["input"]["topic"]
            })

        result = "success"
    else:
        print("No improvement")
        result = "fail"

    memory.append({
        "topic": topic,
        "weakness": weakness,
        "old_score": old_score,
        "new_score": best_score,
        "result": result,
        "time": _now()
    })

    memory = memory[-200:]
    save_memory(memory)

    print("=== END CYCLE ===\n")

if __name__ == "__main__":
    while True:
        try:
            run_cycle()
        except Exception as e:
            print("Error:", e)
        time.sleep(600)


