from fastapi import APIRouter, Body
from datetime import datetime
import os, json

router = APIRouter()

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "untitled")).strip("_")[:80] or "untitled"

def _fallback_script(topic, buyer, promise):
    return (
        f"{topic}\n\n"
        f"For: {buyer}\n"
        f"Promise: {promise}\n\n"
        "Hook: Here is the simplest way to start.\n"
        "Step 1: pick one clear outcome.\n"
        "Step 2: create one useful asset around it.\n"
        "Step 3: post and improve the winner.\n"
        "CTA: Download the package and use it today."
    )

def _write_output(name: str, data):
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

@router.post("/api/founder/full-stack-generate")
def founder_full_stack_generate(payload: dict = Body(...)):
    topic = payload.get("topic", "Faceless TikTok AI starter pack for beginners")
    buyer = payload.get("buyer", "New creators")
    promise = payload.get("promise", "start posting quickly")
    niche = payload.get("niche", "Content Monetization")
    tone = payload.get("tone", "Premium")
    bonus = payload.get("bonus", "hook templates")
    notes = payload.get("notes", "Founder full-stack generate run")

    safe_script = _fallback_script(topic, buyer, promise)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    base_name = f"{_slug(topic)}_{timestamp}"

    try:
        from backend.app.video_factory_engine import build_video_factory_package
    except Exception:
        build_video_factory_package = None

    try:
        from backend.app.body_engine import build_variants, score_package
    except Exception:
        build_variants = None
        score_package = None

    try:
        from backend.app.distribution_engine import build_distribution_package
    except Exception:
        build_distribution_package = None

    package = {}
    if build_video_factory_package:
        try:
            package = build_video_factory_package({
                "topic": topic,
                "buyer": buyer,
                "promise": promise,
                "niche": niche,
                "tone": tone,
                "bonus": bonus,
                "notes": notes
            }) or {}
        except Exception:
            package = {}

    script = package.get("script") or safe_script

    hooks = [
        f"How {buyer} can use {topic} to {promise}",
        f"The beginner shortcut for {topic}",
        f"Most people overcomplicate {topic}. Do this instead.",
        f"Start with this {topic} angle before it gets crowded.",
        f"The fastest way to turn {topic} into action today."
    ]

    cta = f"Download the {topic} package and start to {promise}."

    variants = []
    if build_variants:
        try:
            variants = build_variants(topic, buyer, promise, niche) or []
        except Exception:
            variants = []

    scores = {"overall": 7, "clarity": 7, "virality": 7, "monetization": 7}
    if score_package:
        try:
            titles = [v.get("title", "") for v in variants if isinstance(v, dict)]
            scores = score_package(topic, buyer, promise, niche, tone, script, titles) or scores
        except Exception:
            pass

    distribution = {
        "tiktok": [
            {"hook": hooks[0], "script": script[:220] + ("..." if len(script) > 220 else ""), "cta": cta},
            {"hook": hooks[1], "script": script[:220] + ("..." if len(script) > 220 else ""), "cta": cta},
            {"hook": hooks[2], "script": script[:220] + ("..." if len(script) > 220 else ""), "cta": cta}
        ],
        "youtube": {
            "title": f"{topic} | Full Breakdown",
            "description": f"{topic}\n\nFor: {buyer}\nPromise: {promise}\nNiche: {niche}\nTone: {tone}\nBonus: {bonus}\nNotes: {notes}",
            "cta": cta
        },
        "twitter": [
            hooks[0],
            f"1/ {topic} is easier when you focus on one outcome.",
            f"2/ Audience: {buyer}",
            f"3/ Promise: {promise}",
            f"4/ Bonus: {bonus}",
            f"5/ CTA: {cta}"
        ]
    }

    if build_distribution_package:
        try:
            distribution = build_distribution_package(topic, buyer, promise, niche, script, variants) or distribution
            if "youtube" not in distribution:
                distribution["youtube"] = {
                    "title": f"{topic} | Full Breakdown",
                    "description": f"{topic}\n\nFor: {buyer}\nPromise: {promise}\nCTA: {cta}",
                    "cta": cta
                }
        except Exception:
            pass

    manifest = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "input": {
            "topic": topic,
            "buyer": buyer,
            "promise": promise,
            "niche": niche,
            "tone": tone,
            "bonus": bonus,
            "notes": notes
        },
        "content": {
            "script": script,
            "hooks": hooks,
            "cta": cta
        },
        "scores": scores,
        "variants": variants,
        "assets": {
            "video": package.get("video", ""),
            "thumbnail": package.get("thumbnail", ""),
            "audio": package.get("audio", "")
        },
        "distribution": distribution
    }

    manifest_url = _write_output(f"{base_name}_manifest.json", manifest)
    script_url = _write_output(f"{base_name}_script.txt", script)
    offer_url = _write_output(
        f"{base_name}_offer.txt",
        f"Title: {topic}\nBuyer: {buyer}\nPromise: {promise}\nNiche: {niche}\nTone: {tone}\nBonus: {bonus}\n\nCTA:\n{cta}\n\nHooks:\n- " + "\n- ".join(hooks)
    )

    return {
        "status": "ok",
        "phase": "one-click money engine",
        "manifest_url": manifest_url,
        "script_url": script_url,
        "offer_url": offer_url,
        "content": {
            "script": script,
            "hooks": hooks,
            "cta": cta
        },
        "scores": scores,
        "assets": manifest["assets"],
        "distribution": distribution
    }

