import time, requests, os, json
from datetime import datetime

BASE = os.getenv("PUBLIC_BASE_URL") or "https://semantiqai-backend-production-bcab.up.railway.app"
MEMORY_PATH = "backend/data/self_improver_memory.json"

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

def diagnose(item):
    scores = item.get("scores", {})
    weakest = min(scores, key=scores.get)
    return weakest

def strategy(weakness):
    if weakness == "monetization":
        return {"promise":"make money faster","bonus":"high converting CTA"}
    if weakness == "virality":
        return {"topic_boost":"secret / mistake / hack angle"}
    if weakness == "clarity":
        return {"notes":"simplify explanation and structure"}
    return {}

def already_tried(topic, weakness, memory):
    return any(m["topic"] == topic and m["weakness"] == weakness for m in memory)

def run_cycle():
    print("=== EVOLUTION CYCLE START ===")

    memory = load_memory()

    history = requests.get(f"{BASE}/api/body-loop/history?limit=10").json().get("items",[])
    if not history:
        print("No history")
        return

    # pick weakest performer
    target = sorted(history, key=lambda x: x.get("scores",{}).get("overall",5))[0]
    topic = target.get("topic","")

    weakness = diagnose(target)

    if already_tried(topic, weakness, memory):
        print("Already tried improvement for this weakness, skipping")
        return

    strat = strategy(weakness)

    improved_input = {
        "topic": f"{topic} (optimized {weakness})",
        "buyer": target.get("buyer","Founders"),
        "promise": strat.get("promise","grow faster"),
        "niche": target.get("niche","Content Monetization"),
        "tone": "Premium",
        "bonus": strat.get("bonus","optimized hooks"),
        "notes": strat.get("notes","evolution improvement")
    }

    # run improved version
    new_run = requests.post(f"{BASE}/api/body-loop/run", json=improved_input).json()

    manifest = new_run.get("manifest", {})
    new_score = manifest.get("scores",{}).get("overall",0)
    old_score = target.get("scores",{}).get("overall",0)

    print(f"{weakness} fix | Old: {old_score} → New: {new_score}")

    if new_score > old_score:
        print("Improvement accepted")

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

    else:
        print("No improvement")

    memory.append({
        "topic": topic,
        "weakness": weakness,
        "old_score": old_score,
        "new_score": new_score,
        "timestamp": _now()
    })

    memory = memory[-100:]
    save_memory(memory)

    print("=== EVOLUTION CYCLE END ===\n")

if __name__ == "__main__":
    while True:
        try:
            run_cycle()
        except Exception as e:
            print("Error:", e)
        time.sleep(600)
