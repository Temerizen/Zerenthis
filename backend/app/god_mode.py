import asyncio
import os
import json
import random
from datetime import datetime, timedelta

from backend.app.body_engine import recent_runs
from backend.app.distribution_engine import build_distribution_package, enqueue

MEMORY_PATH = "backend/data/god_mode_memory.json"
COOLDOWN_HOURS = 6
MAX_MEMORY = 300


def _now_dt():
    return datetime.utcnow()


def _now():
    return _now_dt().isoformat() + "Z"


def _parse_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", ""))
    except Exception:
        return None


def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return []
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_memory(data):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data[-MAX_MEMORY:], f, indent=2, ensure_ascii=False)


def weakest(scores):
    return min(["monetization", "virality", "clarity"], key=lambda k: scores.get(k, 5))


def mutation_protocol(weakness):
    if weakness == "monetization":
        return [
            {"promise_prefix": "start making money with", "bonus": "plug-and-play monetization hooks"},
            {"promise_prefix": "turn into a paid offer using", "bonus": "conversion CTA templates"},
            {"promise_prefix": "sell faster with", "bonus": "buyer psychology prompts"},
        ]
    if weakness == "virality":
        return [
            {"topic_prefix": "How to use", "topic_suffix": "before it gets crowded", "bonus": "viral hook bank"},
            {"topic_prefix": "The hidden angle behind", "topic_suffix": "most creators miss", "bonus": "attention reset templates"},
            {"topic_prefix": "Mistakes ruining", "topic_suffix": "and how to fix them", "bonus": "pattern interrupt hooks"},
        ]
    if weakness == "clarity":
        return [
            {"topic_prefix": "Step-by-step", "notes": "Use numbered steps, short sentences, and beginner-safe wording.", "bonus": "clarity checklist"},
            {"topic_prefix": "Simple", "notes": "Explain like the viewer is brand new. Use three clean steps and one concrete example.", "bonus": "plain-English script map"},
            {"topic_prefix": "Beginner breakdown of", "notes": "Reduce fluff, add structure, and end with a direct action plan.", "bonus": "action plan template"},
        ]
    return [{"notes": "optimized", "bonus": "optimized"}]


def _clean_join(*parts):
    return " ".join(str(p).strip() for p in parts if str(p).strip()).strip()


def _structured_clarity_script(topic, buyer, promise, niche, bonus):
    return (
        f"Today we are breaking down {topic}. "
        f"This is for {buyer} who want to {promise} in {niche}. "
        f"Step 1: understand the goal and remove extra complexity. "
        f"Step 2: use one simple method consistently instead of juggling ten ideas. "
        f"Step 3: package the result clearly so the audience instantly understands the value. "
        f"Example: take one idea, turn it into one offer, and present one clear outcome. "
        f"Bonus: use {bonus} to speed up execution. "
        f"Final move: start simple, measure what works, then improve the winner."
    )


def _build_variant(base, weakness, rule):
    v = dict(base)

    topic_prefix = rule.get("topic_prefix", "")
    topic_suffix = rule.get("topic_suffix", "")
    promise_prefix = rule.get("promise_prefix", "")

    if topic_prefix or topic_suffix:
        v["topic"] = _clean_join(topic_prefix, base["topic"], topic_suffix)

    if promise_prefix:
        v["promise"] = _clean_join(promise_prefix, base["topic"]).strip()

    if rule.get("notes"):
        v["notes"] = rule["notes"]

    if rule.get("bonus"):
        v["bonus"] = rule["bonus"]

    if weakness == "clarity":
        v["script"] = _structured_clarity_script(
            v["topic"],
            v["buyer"],
            v["promise"],
            v["niche"],
            v["bonus"],
        )

    return v


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


def _find_recent_memory(memory, topic, weakness):
    matches = [
        m for m in memory
        if m.get("topic") == topic and m.get("weakness") == weakness
    ]
    if not matches:
        return None
    matches.sort(key=lambda m: m.get("time", ""), reverse=True)
    return matches[0]


def _cooldown_active(entry):
    if not entry:
        return False
    if entry.get("result") not in ("fail", "skip"):
        return False
    t = _parse_time(entry.get("time"))
    if not t:
        return False
    return (_now_dt() - t) < timedelta(hours=COOLDOWN_HOURS)


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
    old_score = scores.get("overall", 0)

    print("Target:", topic, "| Weakness:", weakness)

    recent = _find_recent_memory(memory, topic, weakness)
    if _cooldown_active(recent):
        print(f"Cooldown active for {topic} | {weakness}. Skipping for now.")
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

    rules = mutation_protocol(weakness)
    random.shuffle(rules)
    candidates = [_build_variant(base, weakness, rule) for rule in rules]

    best_score = old_score
    best_manifest = None

    for candidate in candidates:
        try:
            manifest = run_body_loop_direct(candidate)
            score = manifest.get("scores", {}).get("overall", 0)
            print("Variant score:", score, "| Topic:", manifest.get("input", {}).get("topic", ""))
            if score > best_score:
                best_score = score
                best_manifest = manifest
        except Exception as e:
            print("Variant failed:", e)

    if best_manifest and best_score > old_score:
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
        print("No improvement. Entering cooldown.")
        result = "fail"

    memory.append({
        "topic": topic,
        "weakness": weakness,
        "old": old_score,
        "new": best_score,
        "result": result,
        "time": _now()
    })
    save_memory(memory)


async def autopilot_loop():
    await asyncio.sleep(45)
    while True:
        try:
            await run_cycle()
        except Exception as e:
            print("Autopilot error:", e)
        await asyncio.sleep(600)

