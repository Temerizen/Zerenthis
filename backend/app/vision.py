from fastapi import APIRouter, UploadFile, File, Body
from pathlib import Path
from datetime import datetime
import os, json, base64

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "vision")).strip("_")[:80] or "vision"

def _save_upload(file: UploadFile) -> Path:
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path

def _write_json(name: str, data: dict) -> str:
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

def _write_text(name: str, data: str) -> str:
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    return f"/api/file/{name}"

def _analyze_image_stub(path: Path):
    # Lightweight heuristic "vision" until full model is plugged in
    name = path.name.lower()

    niche = "Content Monetization"
    if any(x in name for x in ["fitness", "gym", "workout"]):
        niche = "Fitness"
    elif any(x in name for x in ["crypto", "trading", "stock"]):
        niche = "Finance"
    elif any(x in name for x in ["ai", "robot", "tech"]):
        niche = "AI / Tech"

    objects = ["person", "text", "screen", "product"]
    angles = [
        "before/after transformation",
        "step-by-step breakdown",
        "mistakes to avoid",
        "hidden trick most people miss"
    ]

    return {
        "niche": niche,
        "objects_detected": objects,
        "angles": angles
    }

def _build_outputs(topic, buyer, promise, niche, angles):
    hooks = [
        f"How to use {topic} to {promise}",
        f"The {topic} method nobody is using yet",
        f"Start {topic} today with this simple approach"
    ]

    script = (
        f"{topic}\n\nFor: {buyer}\nPromise: {promise}\n\n"
        f"Angle: {angles[0]}\n"
        "Step 1: identify the opportunity\n"
        "Step 2: apply a simple method\n"
        "Step 3: repeat what works\n\n"
        "CTA: Use this idea and start today."
    )

    return hooks, script

@router.post("/api/vision/upload")
async def vision_upload(file: UploadFile = File(...)):
    path = _save_upload(file)
    analysis = _analyze_image_stub(path)

    topic = f"{analysis['niche']} idea from image"
    buyer = "Creators"
    promise = "create content and monetize faster"
    niche = analysis["niche"]

    hooks, script = _build_outputs(topic, buyer, promise, niche, analysis["angles"])

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem = f"{_slug(topic)}_vision_{ts}"

    manifest = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "phase": "vision engine",
        "input_file": path.name,
        "analysis": analysis,
        "output": {
            "topic": topic,
            "buyer": buyer,
            "promise": promise,
            "niche": niche,
            "hooks": hooks,
            "script": script
        }
    }

    manifest_url = _write_json(f"{stem}_manifest.json", manifest)
    script_url = _write_text(f"{stem}_script.txt", script)

    return {
        "status": "ok",
        "phase": "vision engine",
        "analysis": analysis,
        "hooks": hooks,
        "script_url": script_url,
        "manifest_url": manifest_url
    }

@router.post("/api/vision/from-base64")
def vision_from_base64(payload: dict = Body(...)):
    b64 = payload.get("image_base64", "")
    if not b64:
        return {"status": "error", "error": "missing image_base64"}

    try:
        data = base64.b64decode(b64)
        filename = f"vision_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        path = UPLOAD_DIR / filename
        with open(path, "wb") as f:
            f.write(data)
    except Exception as e:
        return {"status": "error", "error": str(e)}

    analysis = _analyze_image_stub(path)

    topic = f"{analysis['niche']} idea from image"
    buyer = "Creators"
    promise = "create content and monetize faster"
    niche = analysis["niche"]

    hooks, script = _build_outputs(topic, buyer, promise, niche, analysis["angles"])

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem = f"{_slug(topic)}_vision_{ts}"

    manifest = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "phase": "vision engine",
        "input_file": path.name,
        "analysis": analysis,
        "output": {
            "topic": topic,
            "buyer": buyer,
            "promise": promise,
            "niche": niche,
            "hooks": hooks,
            "script": script
        }
    }

    manifest_url = _write_json(f"{stem}_manifest.json", manifest)
    script_url = _write_text(f"{stem}_script.txt", script)

    return {
        "status": "ok",
        "phase": "vision engine",
        "analysis": analysis,
        "hooks": hooks,
        "script_url": script_url,
        "manifest_url": manifest_url
    }
