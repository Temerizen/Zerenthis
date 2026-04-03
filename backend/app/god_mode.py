import asyncio, requests, os, json, random
from datetime import datetime

BASE = os.getenv("PUBLIC_BASE_URL") or "https://semantiqai-backend-production-bcab.up.railway.app"
MEMORY_PATH = "backend/data/god_mode_memory.json"

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

def weakest(scores):
    return min(["monetization","virality","clarity"], key=lambda k: scores.get(k,5))

def protocol(weakness):
    if weakness == "monetization":
        return ["make money faster","high converting system","turn content into income"]
    if weakness == "virality":
        return ["secret method","mistakes nobody tells you","growth hack"]
    if weakness == "clarity":
        return ["step by step","simple breakdown","clear system"]
    return ["optimized"]

async def run_cycle():\n    # REALITY FEEDBACK INTEGRATION\n    try:\n        import requests\n        fb = requests.get(BASE + "/api/reality/feedback").json()\n        if fb:\n            top = fb[0]\n            print("Reality signal:", top)\n    except:\n        pass\n
    print("=== GOD MODE SURGEON ===")

    memory = load_memory()

    try:
        history = requests.get(f"{BASE}/api/body-loop/history?limit=10").json().get("items",[])
    except:
        print("Failed to fetch history")
        return

    if not history:
        print("No history yet")
        return

    target = sorted(history, key=lambda x: x.get("scores",{}).get("overall",5))[0]

    topic = target.get("topic","")
    scores = target.get("scores",{})
    weakness = weakest(scores)

    print("Target:", topic, "| Weakness:", weakness)

    if any(m["topic"]==topic and m["weakness"]==weakness and m["result"]=="fail" for m in memory):
        print("Skipping failed pattern")
        return

    base = {
        "topic": topic,
        "buyer": target.get("buyer","Founders"),
        "promise": target.get("promise","grow faster"),
        "niche": target.get("niche","Content Monetization"),
        "tone": "Premium",
        "bonus": "optimized",
        "notes": "god mode run"
    }

    variants = []
    for _ in range(3):
        v = base.copy()
        boost = random.choice(protocol(weakness))

        if weakness == "virality":
            v["topic"] = f"{topic} - {boost}"
        elif weakness == "monetization":
            v["promise"] = boost
        elif weakness == "clarity":
            v["notes"] = boost

        variants.append(v)

    best_score = 0
    best_manifest = None

    for v in variants:
        try:
            res = requests.post(f"{BASE}/api/body-loop/run", json=v).json()
            manifest = res.get("manifest",{})
            score = manifest.get("scores",{}).get("overall",0)

            print("Variant score:", score)

            if score > best_score:
                best_score = score
                best_manifest = manifest
        except:
            continue

    old_score = scores.get("overall",0)

    if best_score > old_score and best_manifest:
        print("Improvement:", old_score, "→", best_score)

        script = best_manifest.get("content",{}).get("script","")
        variants_out = best_manifest.get("variants",[])

        try:
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

        except:
            pass

        result = "success"
    else:
        print("No improvement")
        result = "fail"

    memory.append({
        "topic": topic,
        "weakness": weakness,
        "old": old_score,
        "new": best_score,
        "result": result,
        "time": _now()
    })

    memory = memory[-200:]
    save_memory(memory)

async def autopilot_loop():
    while True:
        try:
            await run_cycle()
        except Exception as e:
            print("Autopilot error:", e)

        await asyncio.sleep(600)  # 10 min cooldown

