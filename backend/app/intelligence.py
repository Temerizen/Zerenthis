from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import os, json

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WEIGHTS_FILE = DATA_DIR / "scoring_weights.json"
WINNERS_FILE = DATA_DIR / "winners.json"
BLACKLIST_FILE = DATA_DIR / "blacklist.json"

DEFAULT_WEIGHTS = {"clarity": 0.3, "virality": 0.3, "monetization": 0.4}

def _now():
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_weights():
    w = _read_json(WEIGHTS_FILE, DEFAULT_WEIGHTS)
    if not isinstance(w, dict):
        return DEFAULT_WEIGHTS.copy()
    for k, v in DEFAULT_WEIGHTS.items():
        w.setdefault(k, v)
    return w

def save_weights(w):
    _write_json(WEIGHTS_FILE, w)

def _norm(w):
    total = sum(max(float(v), 0.0) for v in w.values()) or 1.0
    return {k: float(v)/total for k, v in w.items()}

def compute_weighted(scores: dict, weights: dict) -> float:
    w = _norm(weights)
    return (
        float(scores.get("clarity", 0)) * w.get("clarity", 0) +
        float(scores.get("virality", 0)) * w.get("virality", 0) +
        float(scores.get("monetization", 0)) * w.get("monetization", 0)
    )

def adjust_weights(weights: dict, scores: dict, target: float = 8.0):
    # Increase weight where score is below target, decrease where above
    new_w = dict(weights)
    for k in ("clarity", "virality", "monetization"):
        s = float(scores.get(k, target))
        delta = (target - s) / max(target, 1.0)  # [-1,1] roughly
        new_w[k] = max(0.05, min(0.9, float(new_w.get(k, DEFAULT_WEIGHTS[k])) * (1.0 + 0.5 * delta)))
    return _norm(new_w)

def add_winner(entry: dict):
    data = _read_json(WINNERS_FILE, [])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    data = sorted(data, key=lambda x: x.get("scores", {}).get("overall", 0), reverse=True)[:200]
    _write_json(WINNERS_FILE, data)
    return entry

def add_blacklist(entry: dict):
    data = _read_json(BLACKLIST_FILE, [])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    data = data[-200:]
    _write_json(BLACKLIST_FILE, data)
    return entry

def is_blacklisted(topic: str) -> bool:
    bl = _read_json(BLACKLIST_FILE, [])
    t = (topic or "").lower()
    for e in bl:
        if (e.get("topic") or "").lower() == t:
            return True
    return False

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "untitled")).strip("_")[:80] or "untitled"

def _write_json_output(name: str, data: dict) -> str:
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

@router.post("/api/intel/score")
def intel_score(payload: dict = Body(...)):
    scores = payload.get("scores") or {}
    weights = load_weights()
    overall = compute_weighted(scores, weights)
    return {
        "status": "ok",
        "weights": weights,
        "weighted_overall": overall
    }

@router.post("/api/intel/learn")
def intel_learn(payload: dict = Body(...)):
    scores = payload.get("scores") or {}
    topic = payload.get("topic", "unknown")
    weights = load_weights()
    new_weights = adjust_weights(weights, scores, target=8.0)
    save_weights(new_weights)

    weighted = compute_weighted(scores, new_weights)
    entry = {
        "time": _now(),
        "topic": topic,
        "scores": scores,
        "weighted_overall": weighted,
        "weights": new_weights
    }

    if weighted >= 8.0:
        add_winner(entry)
        decision = "winner"
    elif weighted <= 5.5:
        add_blacklist({"time": entry["time"], "topic": topic, "scores": scores})
        decision = "blacklisted"
    else:
        decision = "neutral"

    return {
        "status": "ok",
        "decision": decision,
        "weights": new_weights,
        "weighted_overall": weighted
    }

@router.post("/api/intel/evolve")
def intel_evolve(payload: dict = Body(...)):
    topic = payload.get("topic", "Faceless TikTok AI starter pack for beginners")
    buyer = payload.get("buyer", "New creators")
    promise = payload.get("promise", "start posting quickly")
    niche = payload.get("niche", "Content Monetization")
    tone = payload.get("tone", "Premium")
    bonus = payload.get("bonus", "hook templates")

    if is_blacklisted(topic):
        return {"status": "skipped", "reason": "blacklisted topic", "topic": topic}

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

    base = {
        "topic": topic,
        "buyer": buyer,
        "promise": promise,
        "niche": niche,
        "tone": tone,
        "bonus": bonus,
        "notes": "intel evolve run"
    }

    package = {}
    if build_video_factory_package:
        try:
            package = build_video_factory_package(base) or {}
        except Exception:
            package = {}

    script = package.get("script") or (
        f"{topic}\n\nFor: {buyer}\nPromise: {promise}\n\n"
        "Step 1: define one outcome.\nStep 2: build one asset.\nStep 3: publish and iterate.\n"
        "CTA: Use the package and execute today."
    )

    variants = []
    if build_variants:
        try:
            variants = build_variants(topic, buyer, promise, niche) or []
        except Exception:
            variants = []

    scores = {"clarity": 7, "virality": 7, "monetization": 7}
    if score_package:
        try:
            titles = [v.get("title", "") for v in variants if isinstance(v, dict)]
            scores = score_package(topic, buyer, promise, niche, tone, script, titles) or scores
        except Exception:
            pass

    weights = load_weights()
    weighted_overall = compute_weighted(scores, weights)

    distribution = {
        "tiktok": [],
        "youtube": {"title": f"{topic} | Full Breakdown", "description": f"{topic} for {buyer}. Promise: {promise}."}
    }
    if build_distribution_package:
        try:
            distribution = build_distribution_package(topic, buyer, promise, niche, script, variants) or distribution
        except Exception:
            pass

    decision = "neutral"
    if weighted_overall >= 8.0:
        decision = "winner"
        add_winner({
            "time": _now(),
            "topic": topic,
            "scores": {**scores, "overall": weighted_overall}
        })
    elif weighted_overall <= 5.5:
        decision = "blacklisted"
        add_blacklist({"time": _now(), "topic": topic, "scores": scores})

    # Learn/update weights from this run
    new_weights = adjust_weights(weights, scores, target=8.0)
    save_weights(new_weights)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = f"{_slug(topic)}_intel_{ts}.json"
    manifest_url = _write_json_output(name, {
        "time": _now(),
        "input": base,
        "scores": scores,
        "weights_before": weights,
        "weights_after": new_weights,
        "weighted_overall": weighted_overall,
        "decision": decision,
        "assets": {
            "video": package.get("video", ""),
            "thumbnail": package.get("thumbnail", ""),
            "audio": package.get("audio", "")
        },
        "distribution": distribution
    })

    return {
        "status": "ok",
        "phase": "intelligence scoring",
        "decision": decision,
        "scores": scores,
        "weights": new_weights,
        "weighted_overall": weighted_overall,
        "manifest_url": manifest_url
    }
