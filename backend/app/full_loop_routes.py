import os
from urllib.parse import quote
from fastapi import APIRouter, Body, Request, HTTPException
from fastapi.responses import FileResponse
from backend.app.video_factory_engine import build_video_factory_package

router = APIRouter(tags=["full-loop"])

OUTPUT_DIR = os.path.abspath("backend/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _safe_name(path: str) -> str:
    return os.path.basename(path or "").strip()

def _asset_url(request: Request, filename: str) -> str:
    public_base = (os.getenv("PUBLIC_BASE_URL") or "https://semantiqai-backend-production-bcab.up.railway.app").rstrip("/")
    return f"{public_base}/api/assets/{quote(filename)}"

def _build_meta(data: dict, script: str) -> dict:
    topic = data.get("topic", "Generated Content")
    buyer = data.get("buyer", "Creators")
    promise = data.get("promise", "grow faster")
    niche = data.get("niche", "Content")
    tone = data.get("tone", "Premium")
    bonus = data.get("bonus", "hook templates")
    notes = data.get("notes", "fast execution")

    hooks = [
        f"How {buyer} can use {topic} to {promise}",
        f"Nobody is talking about this {topic} angle yet",
        f"Use this {topic} method before everyone copies it"
    ]

    caption = f"{topic} for {buyer}. Goal: {promise}. Bonus: {bonus}."
    tiktok = {
        "hooks": hooks,
        "caption": caption,
        "short_script": script[:220] + ("..." if len(script) > 220 else "")
    }

    youtube = {
        "title": f"{topic} | Full Breakdown",
        "description": f"{topic}\n\nFor: {buyer}\nPromise: {promise}\nNiche: {niche}\nTone: {tone}\nBonus: {bonus}\nNotes: {notes}",
        "tags": [topic, niche, buyer, "Zerenthis", "AI content", "automation"]
    }

    monetization = {
        "offer_name": topic,
        "cta": f"Download the {topic} package and start to {promise}.",
        "product_angle": f"A {tone.lower()} offer for {buyer} in {niche}.",
        "bonus": bonus
    }

    evolution = {
        "score_seed": 7,
        "winner_hint": f"If this performs well, create 3 more variations around {topic}.",
        "next_variants": [
            f"{topic} for beginners",
            f"{topic} advanced version",
            f"{topic} mistakes to avoid"
        ]
    }

    return {
        "tiktok": tiktok,
        "youtube": youtube,
        "monetization": monetization,
        "evolution": evolution
    }

@router.get("/api/assets/{filename:path}")
def get_asset(filename: str):
    safe = os.path.basename(filename)
    full_path = os.path.abspath(os.path.join(OUTPUT_DIR, safe))
    if not full_path.startswith(OUTPUT_DIR):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path, filename=safe)

@router.post("/api/full-loop/run")
def run_full_loop(request: Request, data: dict = Body(...)):
    package = build_video_factory_package(data)

    video_name = _safe_name(package.get("video"))
    thumb_name = _safe_name(package.get("thumbnail"))
    audio_name = _safe_name(package.get("audio"))
    script = package.get("script", "")

    meta = _build_meta(data, script)

    return {
        "status": "ok",
        "phase": "full loop activation",
        "input": {
            "topic": data.get("topic", ""),
            "buyer": data.get("buyer", ""),
            "promise": data.get("promise", ""),
            "niche": data.get("niche", ""),
            "tone": data.get("tone", "")
        },
        "assets": {
            "video": package.get("video"),
            "thumbnail": package.get("thumbnail"),
            "audio": package.get("audio"),
            "video_url": _asset_url(request, video_name) if video_name else "",
            "thumbnail_url": _asset_url(request, thumb_name) if thumb_name else "",
            "audio_url": _asset_url(request, audio_name) if audio_name else ""
        },
        "content": {
            "script": script
        },
        "distribution": meta["tiktok"],
        "youtube": meta["youtube"],
        "monetization": meta["monetization"],
        "evolution": meta["evolution"]
    }
