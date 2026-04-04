from fastapi import APIRouter, Request, HTTPException, Body
import os
import json
from datetime import datetime
from urllib.parse import quote

from backend.app.video_factory_engine import build_video_factory_package
from backend.app.body_engine import build_variants, score_package, persist_run, make_manifest
from backend.app.distribution_engine import build_distribution_package, enqueue

router = APIRouter()

OUTPUT_DIR = os.path.abspath("backend/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _now():
    return datetime.utcnow().isoformat() + "Z"

def is_founder(request: Request):
    key = os.getenv("FOUNDER_KEY", "")
    return bool(key) and request.headers.get("x-founder-key") == key

def _asset_url(filename: str) -> str:
    public_base = (os.getenv("PUBLIC_BASE_URL") or "https://api.zerenthis.com").rstrip("/")
    safe = quote(os.path.basename(filename or ""))
    return f"{public_base}/api/assets/{safe}" if safe else ""

@router.get("/api/founder/ping")
def founder_ping(request: Request):
    if not is_founder(request):
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"status": "founder access confirmed"}

@router.post("/api/founder/toggle-autopilot")
def toggle_autopilot(request: Request):
    if not is_founder(request):
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"autopilot": "toggled (placeholder)"}

@router.post("/api/founder/cash-machine")
def founder_cash_machine(request: Request, data: dict = Body(...)):
    if not is_founder(request):
        raise HTTPException(status_code=403, detail="Not authorized")

    payload = {
        "topic": data.get("topic", "Faceless TikTok AI starter pack for beginners"),
        "buyer": data.get("buyer", "New creators"),
        "promise": data.get("promise", "start posting quickly"),
        "niche": data.get("niche", "Content Monetization"),
        "tone": data.get("tone", "Premium"),
        "bonus": data.get("bonus", "hook templates"),
        "notes": data.get("notes", "Founder cash-machine run")
    }

    package = build_video_factory_package(payload)
    script = package.get("script") or (
        f"{payload['topic']}. For {payload['buyer']}. Promise: {payload['promise']}. "
        f"Use one simple method, package one clear outcome, and post consistently."
    )

    variants = build_variants(
        payload["topic"],
        payload["buyer"],
        payload["promise"],
        payload["niche"]
    )

    scores = score_package(
        payload["topic"],
        payload["buyer"],
        payload["promise"],
        payload["niche"],
        payload["tone"],
        script,
        [v["title"] for v in variants]
    )

    distribution = build_distribution_package(
        payload["topic"],
        payload["buyer"],
        payload["promise"],
        payload["niche"],
        script,
        variants
    )

    monetization = {
        "offer_name": payload["topic"],
        "cta": f"Download the {payload['topic']} package and start to {payload['promise']}.",
        "product_angle": f"A {payload['tone'].lower()} offer for {payload['buyer']} in {payload['niche']}.",
        "bonus": payload["bonus"]
    }

    youtube = {
        "title": f"{payload['topic']} | Full Breakdown",
        "description": f"{payload['topic']}\n\nFor: {payload['buyer']}\nPromise: {payload['promise']}\nNiche: {payload['niche']}\nTone: {payload['tone']}\nBonus: {payload['bonus']}\nNotes: {payload['notes']}",
        "tags": [payload["topic"], payload["niche"], payload["buyer"], "Zerenthis", "AI content", "automation"]
    }

    evolution = {
        "score_seed": 7,
        "winner_hint": f"If this performs well, create 3 more variations around {payload['topic']}.",
        "next_variants": [
            f"{payload['topic']} for beginners",
            f"{payload['topic']} advanced version",
            f"{payload['topic']} mistakes to avoid"
        ]
    }

    manifest = make_manifest(
        payload,
        {
            "video": package.get("video", ""),
            "thumbnail": package.get("thumbnail", ""),
            "audio": package.get("audio", ""),
            "script": script
        },
        {
            "tiktok": distribution.get("tiktok", []),
            "youtube": youtube,
            "monetization": monetization,
            "evolution": evolution
        },
        variants,
        scores
    )

    persist_run({
        "created_at": manifest["created_at"],
        "topic": manifest["input"]["topic"],
        "buyer": manifest["input"]["buyer"],
        "promise": manifest["input"]["promise"],
        "niche": manifest["input"]["niche"],
        "tone": manifest["input"]["tone"],
        "scores": manifest["scores"],
        "assets": manifest["assets"],
        "distribution": manifest["distribution"],
        "youtube": manifest["youtube"],
        "monetization": manifest["monetization"],
        "variants": manifest["variants"]
    })

    manifest_name = f"cash_machine_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    manifest_path = os.path.join(OUTPUT_DIR, manifest_name)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    queued = []
    for item in distribution.get("tiktok", [])[:3]:
        queued.append(enqueue({
            "platform": "tiktok",
            "topic": payload["topic"],
            "content": item
        }))

    queued.append(enqueue({
        "platform": "youtube",
        "topic": payload["topic"],
        "content": distribution.get("youtube_long", {})
    }))

    return {
        "status": "ok",
        "phase": "founder cash machine",
        "input": payload,
        "scores": scores,
        "assets": {
            "video": package.get("video", ""),
            "thumbnail": package.get("thumbnail", ""),
            "audio": package.get("audio", ""),
            "video_url": _asset_url(package.get("video", "")),
            "thumbnail_url": _asset_url(package.get("thumbnail", "")),
            "audio_url": _asset_url(package.get("audio", "")),
            "manifest_file": manifest_name,
            "manifest_url": _asset_url(manifest_name)
        },
        "content": {
            "script": script
        },
        "distribution": distribution,
        "youtube": youtube,
        "monetization": monetization,
        "evolution": evolution,
        "queue": queued
    }

