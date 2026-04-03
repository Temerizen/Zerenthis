import asyncio, requests, os, json, random
from datetime import datetime

PUBLIC_BASE = (os.getenv("PUBLIC_BASE_URL") or "https://semantiqai-backend-production-bcab.up.railway.app").rstrip("/")
LOCAL_BASE = "http://127.0.0.1:8080"
MEMORY_PATH = "backend/data/god_mode_memory.json"

def _now():
    return datetime.utcnow().isoformat() + "Z"

def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return []
    try:
        return json.load(open(MEMORY_PATH, "r"))
    except:
        return []

def save_memory(data):
    json.dump(data, open(MEMORY_PATH, "w"), indent=2)

def weakest(scores):
    return min(["monetization", "virality", "clarity"], key=lambda k: scores.get(k, 5))

def protocol(weakness):
    if weakness == "monetization":
        return ["make money faster", "high converting system", "turn content into income"]
    if weakness == "virality":
        return ["secret method", "mistakes nobody tells you", "growth hack"]
    if weakness == "clarity":
        return ["step by step", "simple breakdown", "clear system"]
    return ["optimized"]

def get_json(path, prefer_local=True):
    bases = [LOCAL_BASE, PUBLIC_BASE] if prefer_local else [PUBLIC_BASE, LOCAL_BASE]
    last_error = None
    for base in bases:
        try:
            return requests.get(f"{base}{path}", timeout=20).json()
        except Exception as e:
            last_error = e
    raise last_error

def post_json(path, payload, prefer_local=True):
    bases = [LOCAL_BASE, PUBLIC_BASE] if prefer_local else [PUBLIC_BASE, LOCAL_BASE]
    last_error = None
    for base in bases:
        try:
            return requests.post(f"{base}{path}", json=payload, timeout=60).json()
        except Exception as e:
            last_error = e
    raise last_error

async def run_cycle():
    print("=== GOD MODE SURGEON ===")

    memory = load_memory()

    try:
        history_res = get_json("/api/body-loop/history?limit=10")
        history = history_res.get("items", [])
    except Exception as e:
        print("Failed to fetch history:", e)
        return

    if not history:
        print("No history yet")
        return

    try:
        fb = get_json("/api/reality/feedback")
        if fb:
            print("Reality signal:", fb[0] if isinstance(fb, list) else fb)
    except:
        pass

    target = sorted(history, key=lambda x: x.get("scores", {}).get("overall", 5))[0]
    topic = target.get("topic", "")
    scores = target.get("scores", {})
    weakness = weakest(scores)

    print("Target:", topic, "| Weakness:", weakness)

    if any(m["topic"] == topic and m["weakness"] == weakness and m["result"] == "fail" for m in memory):
        print("Skipping failed pattern")
        return

    base = {
        "topic": topic,
        "buyer": target.get("buyer", "Founders"),
        "promise": target.get("promise", "grow faster"),
        "niche": target.get("niche", "Content Monetization"),
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
            res = post_json("/api/body-loop/run", v)
            manifest = res.get("manifest", {})
            score = manifest.get("scores", {}).get("overall", 0)
            print("Variant score:", score)
            if score > best_score:
                best_score = score
                best_manifest = manifest
        except Exception as e:
            print("Variant failed:", e)

    old_score = scores.get("overall", 0)

    if best_score > old_score and best_manifest:
        print("Improvement:", old_score, "->", best_score)
        script = best_manifest.get("content", {}).get("script", "")
        variants_out = best_manifest.get("variants", [])
        try:
            dist = post_json("/api/distribution/build", {
                "topic": best_manifest["input"]["topic"],
                "buyer": best_manifest["input"]["buyer"],
                "promise": best_manifest["input"]["promise"],
                "niche": best_manifest["input"]["niche"],
                "script": script,
                "variants": variants_out
            })
            if dist.get("tiktok"):
                post_json("/api/distribution/queue", {
                    "platform": "tiktok",
                    "content": dist["tiktok"][0],
                    "topic": best_manifest["input"]["topic"]
                })
        except Exception as e:
            print("Distribution failed:", e)
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
    await asyncio.sleep(45)
    while True:
        try:
            await run_cycle()
        except Exception as e:
            print("Autopilot error:", e)
        await asyncio.sleep(600)
