from fastapi import APIRouter, Body, UploadFile, File
from pathlib import Path
from datetime import datetime
import os, json, base64, re

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "vision")).strip("_")[:80] or "vision"

def _write_json(name: str, data: dict):
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

def _write_text(name: str, text: str):
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return f"/api/file/{name}"

def _save_upload(file: UploadFile) -> Path:
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path

def _fake_ocr_from_name(name: str):
    # placeholder OCR logic until real model
    name = name.lower()
    extracted = []
    if "tiktok" in name:
        extracted.append("TikTok growth hack")
    if "ai" in name:
        extracted.append("AI automation")
    if "money" in name:
        extracted.append("make money online")
    if not extracted:
        extracted.append("general content strategy")
    return extracted

def _analyze_visual(path: Path):
    name = path.name.lower()

    niche = "Content Monetization"
    if "fitness" in name:
        niche = "Fitness"
    elif "crypto" in name:
        niche = "Finance"
    elif "ai" in name:
        niche = "AI / Tech"

    ocr_text = _fake_ocr_from_name(name)

    angles = [
        "before/after",
        "step-by-step",
        "hidden hack",
        "mistake to avoid"
    ]

    return {
        "niche": niche,
        "ocr": ocr_text,
        "angles": angles,
        "confidence": 0.65
    }

def _detect_weakness(analysis):
    weaknesses = []
    if len(analysis["ocr"]) < 1:
        weaknesses.append("no clear message")
    if analysis["confidence"] < 0.7:
        weaknesses.append("low confidence signal")
    return weaknesses

def _generate_offer_from_visual(analysis):
    topic = f"{analysis['niche']} visual strategy"
    buyer = "Creators"
    promise = "turn visuals into monetizable content"

    hooks = [
        f"Turn this {analysis['niche']} idea into income",
        "Most people miss this visual opportunity",
        "Steal this simple visual strategy"
    ]

    script = (
        f"{topic}\n\n"
        f"Detected: {', '.join(analysis['ocr'])}\n\n"
        "Step 1: Identify what works visually\n"
        "Step 2: Repurpose into content\n"
        "Step 3: Attach monetization angle\n\n"
        "CTA: Execute immediately."
    )

    return topic, buyer, promise, hooks, script

@router.post("/api/vision/inspect")
async def vision_inspect(file: UploadFile = File(...)):
    path = _save_upload(file)
    analysis = _analyze_visual(path)
    weaknesses = _detect_weakness(analysis)

    topic, buyer, promise, hooks, script = _generate_offer_from_visual(analysis)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem = f"{_slug(topic)}_inspect_{ts}"

    manifest = {
        "phase": "vision hardening",
        "file": path.name,
        "analysis": analysis,
        "weaknesses": weaknesses,
        "generated": {
            "topic": topic,
            "hooks": hooks,
            "script": script
        }
    }

    manifest_url = _write_json(f"{stem}_manifest.json", manifest)
    script_url = _write_text(f"{stem}_script.txt", script)

    return {
        "status": "ok",
        "analysis": analysis,
        "weaknesses": weaknesses,
        "hooks": hooks,
        "script_url": script_url,
        "manifest_url": manifest_url
    }

@router.post("/api/vision/competitor-scan")
def competitor_scan(payload: dict = Body(...)):
    text = payload.get("text", "")
    words = re.findall(r"\w+", text.lower())

    angles = []
    if "fast" in words:
        angles.append("speed angle")
    if "easy" in words:
        angles.append("simplicity angle")
    if "money" in words:
        angles.append("monetization angle")

    weaknesses = []
    if len(words) < 20:
        weaknesses.append("low information density")
    if "unique" not in words:
        weaknesses.append("no differentiation")

    improved = text + "\n\nImprovement:\nAdd a stronger promise and clearer monetization outcome."

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem = f"competitor_scan_{ts}"

    report = {
        "phase": "competitor analysis",
        "input": text,
        "angles_detected": angles,
        "weaknesses": weaknesses,
        "improved_version": improved
    }

    report_url = _write_json(f"{stem}.json", report)

    return {
        "status": "ok",
        "angles": angles,
        "weaknesses": weaknesses,
        "report_url": report_url
    }

@router.post("/api/vision/simulate")
def simulate(payload: dict = Body(...)):
    topic = payload.get("topic", "AI content strategy")
    score = {
        "clarity": 7,
        "virality": 6,
        "monetization": 8
    }

    predicted_success = (score["clarity"] + score["virality"] + score["monetization"]) / 3

    result = {
        "phase": "simulation",
        "topic": topic,
        "scores": score,
        "predicted_success": predicted_success,
        "decision": "proceed" if predicted_success > 6.5 else "revise"
    }

    return {
        "status": "ok",
        "simulation": result
    }
