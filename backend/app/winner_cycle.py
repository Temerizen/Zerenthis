from fastapi import APIRouter, Body
from datetime import datetime
import os, json

router = APIRouter()

OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "untitled")).strip("_")[:80] or "untitled"

def _write_json(name: str, data: dict) -> str:
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

def _write_text(name: str, data: str) -> str:
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    return f"/api/file/{name}"

@router.post("/api/founder/run-winner-cycle")
def run_winner_cycle(payload: dict = Body(default={})):
    try:
        from backend.app.body_engine import recent_runs, build_variants, score_package
    except Exception:
        return {"status": "error", "error": "body_engine not available"}

    try:
        from backend.app.video_factory_engine import build_video_factory_package
    except Exception:
        build_video_factory_package = None

    try:
        from backend.app.distribution_engine import build_distribution_package, enqueue
    except Exception:
        build_distribution_package = None
        def enqueue(item): return {"status": "skipped", "item": item}

    try:
        from backend.app.winners import add_winner
    except Exception:
        def add_winner(entry): return None

    runs = recent_runs(25) or []
    if not runs:
        base = {
            "topic": payload.get("topic", "Faceless TikTok AI starter pack for beginners"),
            "buyer": payload.get("buyer", "New creators"),
            "promise": payload.get("promise", "start posting quickly"),
            "niche": payload.get("niche", "Content Monetization"),
            "tone": payload.get("tone", "Premium"),
            "bonus": payload.get("bonus", "hook templates"),
            "notes": payload.get("notes", "Winner cycle fallback run")
        }
    else:
        best = sorted(runs, key=lambda r: r.get("scores", {}).get("overall", 0), reverse=True)[0]
        base = {
            "topic": payload.get("topic") or best.get("topic", "Untitled"),
            "buyer": payload.get("buyer") or best.get("buyer", "Creators"),
            "promise": payload.get("promise") or best.get("promise", "grow faster"),
            "niche": payload.get("niche") or best.get("niche", "Content Monetization"),
            "tone": payload.get("tone") or best.get("tone", "Premium"),
            "bonus": payload.get("bonus", "winner hooks"),
            "notes": payload.get("notes", "Winner cycle regeneration")
        }

    package = {}
    if build_video_factory_package:
        try:
            package = build_video_factory_package(base) or {}
        except Exception:
            package = {}

    script = package.get("script") or (
        f"{base['topic']}\n\n"
        f"For: {base['buyer']}\n"
        f"Promise: {base['promise']}\n\n"
        "Hook: This is the winner angle to build on.\n"
        "Step 1: keep the promise clear.\n"
        "Step 2: keep the execution simple.\n"
        "Step 3: repeat the angle that already scores well.\n"
        "CTA: Use this package and publish the strongest version first."
    )

    try:
        variants = build_variants(base["topic"], base["buyer"], base["promise"], base["niche"]) or []
    except Exception:
        variants = []

    try:
        titles = [v.get("title", "") for v in variants if isinstance(v, dict)]
        scores = score_package(base["topic"], base["buyer"], base["promise"], base["niche"], base["tone"], script, titles) or {}
    except Exception:
        scores = {"overall": 7, "monetization": 7, "virality": 7, "clarity": 7}

    distribution = {
        "tiktok": [],
        "youtube_long": {
            "title": f"{base['topic']} FULL GUIDE",
            "description": f"{base['topic']} for {base['buyer']}. Promise: {base['promise']}.",
            "outline": ["Intro", "Core breakdown", "Steps", "Mistakes", "CTA"]
        }
    }
    if build_distribution_package:
        try:
            distribution = build_distribution_package(base["topic"], base["buyer"], base["promise"], base["niche"], script, variants) or distribution
        except Exception:
            pass

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem = f"{_slug(base['topic'])}_winner_cycle_{timestamp}"

    manifest = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "phase": "winner cycle",
        "input": base,
        "scores": scores,
        "content": {
            "script": script,
            "cta": f"Download the {base['topic']} package and start to {base['promise']}."
        },
        "assets": {
            "video": package.get("video", ""),
            "thumbnail": package.get("thumbnail", ""),
            "audio": package.get("audio", "")
        },
        "variants": variants,
        "distribution": distribution
    }

    manifest_url = _write_json(f"{stem}_manifest.json", manifest)
    script_url = _write_text(f"{stem}_script.txt", script)

    queued = []
    for item in (distribution.get("tiktok", []) or [])[:3]:
        queued.append(enqueue({
            "platform": "tiktok",
            "topic": base["topic"],
            "content": item
        }))

    queued.append(enqueue({
        "platform": "youtube",
        "topic": base["topic"],
        "content": distribution.get("youtube_long", {})
    }))

    winner_entry = {
        "created_at": manifest["created_at"],
        "topic": base["topic"],
        "buyer": base["buyer"],
        "promise": base["promise"],
        "niche": base["niche"],
        "scores": scores,
        "manifest_url": manifest_url,
        "script_url": script_url
    }
    try:
        add_winner(winner_entry)
    except Exception:
        pass

    return {
        "status": "ok",
        "phase": "winner cycle",
        "input": base,
        "scores": scores,
        "manifest_url": manifest_url,
        "script_url": script_url,
        "assets": manifest["assets"],
        "distribution": distribution,
        "queue": queued
    }

