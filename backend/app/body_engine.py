import os
import json
from datetime import datetime
from typing import List, Dict

DATA_DIR = "backend/data"
RUNS_PATH = os.path.join(DATA_DIR, "full_loop_runs.json")
os.makedirs(DATA_DIR, exist_ok=True)

def _now():
    return datetime.utcnow().isoformat() + "Z"

def _load_runs() -> List[Dict]:
    if not os.path.exists(RUNS_PATH):
        return []
    try:
        with open(RUNS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_runs(runs: List[Dict]):
    with open(RUNS_PATH, "w", encoding="utf-8") as f:
        json.dump(runs, f, indent=2, ensure_ascii=False)

def _clamp(n: int) -> int:
    return max(1, min(10, n))

def score_package(topic: str, buyer: str, promise: str, niche: str, tone: str, script: str, variants: List[str]) -> Dict:
    topic = topic or ""
    buyer = buyer or ""
    promise = promise or ""
    niche = niche or ""
    tone = tone or ""
    script = script or ""

    monetization = 5
    virality = 5
    clarity = 5

    if promise:
        monetization += 1
        clarity += 1
    if buyer:
        monetization += 1
    if niche:
        monetization += 1
    if len(topic.split()) >= 2:
        virality += 1
    if len(script) > 60:
        clarity += 1
    if len(script) > 140:
        virality += 1
    if "how" in topic.lower() or "secret" in topic.lower() or "mistake" in topic.lower():
        virality += 1
    if tone.lower() in ("premium", "bold", "elite"):
        monetization += 1
    if len(variants) >= 3:
        virality += 1

    monetization = _clamp(monetization)
    virality = _clamp(virality)
    clarity = _clamp(clarity)
    overall = round((monetization + virality + clarity) / 3, 2)

    return {
        "overall": overall,
        "monetization": monetization,
        "virality": virality,
        "clarity": clarity,
        "reason": f"Offer strength from buyer/promise/niche, attention strength from topic/variants, clarity from script depth."
    }

def build_variants(topic: str, buyer: str, promise: str, niche: str) -> List[Dict]:
    topic = topic or "Generated Content"
    buyer = buyer or "Creators"
    promise = promise or "grow faster"
    niche = niche or "Content"

    variant_titles = [
        f"{topic} for beginners",
        f"{topic} advanced version",
        f"{topic} mistakes to avoid",
        f"How {buyer} can use {topic}",
        f"{topic} in {niche}"
    ]

    variants = []
    for i, title in enumerate(variant_titles, start=1):
        variants.append({
            "id": i,
            "title": title,
            "hook": f"{title} can help {buyer} {promise}.",
            "caption": f"{title}. For {buyer}. Goal: {promise}.",
            "angle": f"A variation of {topic} positioned for {buyer} in {niche}."
        })
    return variants

def persist_run(record: Dict) -> Dict:
    runs = _load_runs()
    runs.insert(0, record)
    runs = runs[:100]
    _save_runs(runs)
    return record

def recent_runs(limit: int = 10) -> List[Dict]:
    runs = _load_runs()
    return runs[:max(1, min(limit, 50))]

def make_manifest(input_data: Dict, package: Dict, meta: Dict, variants: List[Dict], scores: Dict) -> Dict:
    manifest = {
        "created_at": _now(),
        "phase": "mega body sweep",
        "input": {
            "topic": input_data.get("topic", ""),
            "buyer": input_data.get("buyer", ""),
            "promise": input_data.get("promise", ""),
            "niche": input_data.get("niche", ""),
            "tone": input_data.get("tone", ""),
            "bonus": input_data.get("bonus", ""),
            "notes": input_data.get("notes", "")
        },
        "assets": {
            "video": package.get("video", ""),
            "thumbnail": package.get("thumbnail", ""),
            "audio": package.get("audio", "")
        },
        "content": {
            "script": package.get("script", "")
        },
        "distribution": meta.get("tiktok", {}),
        "youtube": meta.get("youtube", {}),
        "monetization": meta.get("monetization", {}),
        "evolution": meta.get("evolution", {}),
        "variants": variants,
        "scores": scores
    }
    return manifest

