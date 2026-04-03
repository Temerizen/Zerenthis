import asyncio, os, json, random
from datetime import datetime

from backend.app.body_engine import recent_runs
from backend.app.distribution_engine import build_distribution_package, enqueue

MEMORY_PATH = "backend/data/god_mode_memory.json"

def _now():
    return datetime.utcnow().isoformat() + "Z"

def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return []
    try:
        return json.load(open(MEMORY_PATH, "r", encoding="utf-8"))
    except:
        return []

def save_memory(data):
    json.dump(data, open(MEMORY_PATH, "w", encoding="utf-8"), indent=2)

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

def run_body_loop_direct(data: dict):
    from backend.app.video_factory_engine import build_video_factory_package
    from backend.app.body_engine import build_variants, score_package, persist_run, make_manifest

    package = build_video_factory_package(data)
    script = package.get("script", "")

    topic = data.get("topic", "Generated Content")
    buyer = data.get("buyer", "Creators")
    promise = data.get("promise", "grow faster")
    niche = data.get("niche", "Content")
    tone = data.get("tone", "Premium")
    bonus = data.get("bonus", "hook templates")
    notes = data.get("notes", "fast execution")

    meta = {
        "tiktok": {
            "hooks": [
                f"How {buyer} can use {topic} to {promise}",
                f"Nobody is talking about this {topic} angle yet",
                f"Use this {topic} method before everyone copies it"
            ],
            "caption": f"{topic} for {buyer}. Goal: {promise}. Bonus: {bonus}.",
            "short_script": script[:220] + ("..." if len(script) > 220 else "")
        },
        "youtube": {
            "title": f"{topic} | Full Breakdown",
            "description": f"{topic}\n\nFor: {buyer}\nPromise: {promise}\nNiche: {niche}\nTone: {tone}\nBonus: {bonus}\nNotes: {notes}",
            "tags": [topic, niche, buyer, "Zerenthis", "AI content", "automation"]
        },
        "monetization": {
            "offer_name": topic,
            "cta": f"Download the {topic} package and start to {promise}.",
            "product_angle": f"A {tone.lower()} offer for {buyer} in {niche}.",
            "bonus": bonus
        },
        "evolution": {
            "score_seed": 7,
            "winner_hint": f"If this performs well, create 3 more variations around {topic}.",
            "next_variants": [
                f"{topic} for beginners",
                f"{topic} advanced version",
                f"{topic} mistakes to avoid"
            ]
        }
    }

    variants = build_variants(topic, buyer, promise, niche)
    scores = score_package(
        topic,
        buyer,
        promise,
        niche,
        tone,
        script,
        [v["title"] for v in variants]
    )

    manifest = make_manifest(data, package, meta, variants, scores)

    record = {
        "created_at": manifest["created_at"],
        "topic": manifest["input"]["topic"],
        "buyer": manifest["input"]["buyer"],
        "promise": manifest["input"]["promise"],
        "niche": manifest["input"]["niche"],
        "tone": manifest["input"]["tone"],
        "scores": scores,
        "assets": manifest["assets"],
        "distribution": manifest["distribution"],
        "youtube": manifest["youtube"],
        "monetization": manifest["monetization"],
        "variants": manifest["variants"]
    }
    persist_run(record)
    return manifest

async def run_cycle():
    print("=== GOD MODE SURGEON ===")

    memory = load_memory()
    history = recent_runs(10)

    if not history:
        print("No history yet")
        return

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
            manifest = run_body_loop_direct(v)
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

        dist = build_distribution_package(
            best_manifest["input"]["topic"],
            best_manifest["input"]["buyer"],
            best_manifest["input"]["promise"],
            best_manifest["input"]["niche"],
            best_manifest["content"]["script"],
            best_manifest["variants"]
        )

        if dist.get("tiktok"):
            enqueue({
                "platform": "tiktok",
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
