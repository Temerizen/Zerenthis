from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import os, json, math

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PATTERNS_FILE = DATA_DIR / "learning_patterns.json"
ANOMALIES_FILE = DATA_DIR / "anomalies.json"
LEARNING_LOG_FILE = DATA_DIR / "learning_log.json"

DEFAULT_PATTERNS = {
    "winning_keywords": {},
    "losing_keywords": {},
    "winning_buyers": {},
    "losing_buyers": {},
    "winning_niches": {},
    "losing_niches": {},
    "runs": 0
}

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

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "learning")).strip("_")[:80] or "learning"

def _tokenize(text: str):
    raw = (text or "").lower().replace("-", " ").replace("/", " ")
    words = []
    for w in raw.split():
        w = "".join(ch for ch in w if ch.isalnum())
        if len(w) >= 3:
            words.append(w)
    return words[:40]

def _inc(bucket: dict, key: str, amount: int = 1):
    if not key:
        return
    bucket[key] = int(bucket.get(key, 0)) + amount

def _top_items(bucket: dict, limit: int = 12):
    return sorted(bucket.items(), key=lambda x: x[1], reverse=True)[:limit]

def load_patterns():
    data = _read_json(PATTERNS_FILE, DEFAULT_PATTERNS.copy())
    if not isinstance(data, dict):
        data = DEFAULT_PATTERNS.copy()
    for k, v in DEFAULT_PATTERNS.items():
        data.setdefault(k, v if not isinstance(v, dict) else {})
    return data

def save_patterns(data: dict):
    _write_json(PATTERNS_FILE, data)

def append_learning_log(entry: dict):
    data = _read_json(LEARNING_LOG_FILE, [])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    data = data[-300:]
    _write_json(LEARNING_LOG_FILE, data)

def append_anomaly(entry: dict):
    data = _read_json(ANOMALIES_FILE, [])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    data = data[-300:]
    _write_json(ANOMALIES_FILE, data)

def learn_from_result(topic: str, buyer: str, niche: str, scores: dict):
    data = load_patterns()
    overall = float(scores.get("overall", (float(scores.get("clarity", 0)) + float(scores.get("virality", 0)) + float(scores.get("monetization", 0))) / 3 if scores else 0))
    words = _tokenize(topic)

    is_winner = overall >= 8.0
    is_loser = overall <= 5.8

    if is_winner:
        for w in words:
            _inc(data["winning_keywords"], w, 1)
        _inc(data["winning_buyers"], (buyer or "").strip().lower(), 1)
        _inc(data["winning_niches"], (niche or "").strip().lower(), 1)

    if is_loser:
        for w in words:
            _inc(data["losing_keywords"], w, 1)
        _inc(data["losing_buyers"], (buyer or "").strip().lower(), 1)
        _inc(data["losing_niches"], (niche or "").strip().lower(), 1)

    data["runs"] = int(data.get("runs", 0)) + 1
    save_patterns(data)

    entry = {
        "time": _now(),
        "topic": topic,
        "buyer": buyer,
        "niche": niche,
        "scores": scores,
        "winner": is_winner,
        "loser": is_loser
    }
    append_learning_log(entry)
    return {
        "stored": True,
        "winner": is_winner,
        "loser": is_loser,
        "runs": data["runs"]
    }

def suggest_topic_upgrade(topic: str, buyer: str, niche: str):
    data = load_patterns()
    words = _tokenize(topic)
    good = data.get("winning_keywords", {})
    bad = data.get("losing_keywords", {})

    good_bias = [w for w, _ in _top_items(good, 8)]
    bad_bias = [w for w, _ in _top_items(bad, 8)]

    kept = [w for w in words if good.get(w, 0) >= bad.get(w, 0)]
    if not kept:
        kept = words[:3]

    add_word = ""
    for candidate in good_bias:
        if candidate not in kept:
            add_word = candidate
            break

    buyer_bias = _top_items(data.get("winning_buyers", {}), 3)
    niche_bias = _top_items(data.get("winning_niches", {}), 3)

    new_topic = " ".join([w for w in kept if w not in bad_bias[:3]]).strip()
    if add_word:
        new_topic = f"{new_topic} {add_word}".strip()
    if not new_topic:
        new_topic = topic

    suggested_buyer = buyer
    if buyer_bias and (buyer or "").strip().lower() not in dict(buyer_bias):
        suggested_buyer = buyer_bias[0][0].title()

    suggested_niche = niche
    if niche_bias and (niche or "").strip().lower() not in dict(niche_bias):
        suggested_niche = niche_bias[0][0].title()

    return {
        "suggested_topic": new_topic.title(),
        "suggested_buyer": suggested_buyer,
        "suggested_niche": suggested_niche,
        "top_winning_keywords": good_bias,
        "top_losing_keywords": bad_bias
    }

def detect_anomalies(topic: str, buyer: str, niche: str, scores: dict):
    anomalies = []

    clarity = float(scores.get("clarity", 0))
    virality = float(scores.get("virality", 0))
    monetization = float(scores.get("monetization", 0))
    overall = float(scores.get("overall", (clarity + virality + monetization) / 3 if scores else 0))

    if len(_tokenize(topic)) < 3:
        anomalies.append({"type": "weak_topic_density", "detail": "Topic is too short or vague."})
    if clarity < 6:
        anomalies.append({"type": "clarity_risk", "detail": "Output may be too vague or poorly structured."})
    if monetization < 6:
        anomalies.append({"type": "monetization_risk", "detail": "Offer angle may be weak for direct sales."})
    if virality < 6:
        anomalies.append({"type": "virality_risk", "detail": "Hook pattern may be too bland for distribution."})
    if overall < 6:
        anomalies.append({"type": "overall_drop", "detail": "This run is under safe performance threshold."})

    data = load_patterns()
    losing_words = set(w for w, n in _top_items(data.get("losing_keywords", {}), 20) if n >= 2)
    overlap = [w for w in _tokenize(topic) if w in losing_words]
    if overlap:
        anomalies.append({"type": "losing_pattern_overlap", "detail": f"Topic overlaps weak historical patterns: {', '.join(overlap[:8])}"})

    buyer_key = (buyer or "").strip().lower()
    niche_key = (niche or "").strip().lower()
    if data.get("losing_buyers", {}).get(buyer_key, 0) >= 3:
        anomalies.append({"type": "buyer_pattern_risk", "detail": f"Buyer profile has repeated weak history: {buyer}"})
    if data.get("losing_niches", {}).get(niche_key, 0) >= 3:
        anomalies.append({"type": "niche_pattern_risk", "detail": f"Niche has repeated weak history: {niche}"})

    entry = {
        "time": _now(),
        "topic": topic,
        "buyer": buyer,
        "niche": niche,
        "scores": scores,
        "anomalies": anomalies
    }
    if anomalies:
        append_anomaly(entry)

    return {
        "count": len(anomalies),
        "anomalies": anomalies
    }

def _write_output(name: str, data: dict):
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

@router.post("/api/learning/ingest")
def learning_ingest(payload: dict = Body(...)):
    topic = payload.get("topic", "unknown")
    buyer = payload.get("buyer", "creators")
    niche = payload.get("niche", "content monetization")
    scores = payload.get("scores", {})

    learned = learn_from_result(topic, buyer, niche, scores)
    anomalies = detect_anomalies(topic, buyer, niche, scores)
    upgrade = suggest_topic_upgrade(topic, buyer, niche)

    return {
        "status": "ok",
        "phase": "learning ingest",
        "learned": learned,
        "anomalies": anomalies,
        "upgrade": upgrade
    }

@router.post("/api/learning/anomaly-scan")
def learning_anomaly_scan(payload: dict = Body(...)):
    topic = payload.get("topic", "unknown")
    buyer = payload.get("buyer", "creators")
    niche = payload.get("niche", "content monetization")
    scores = payload.get("scores", {})
    result = detect_anomalies(topic, buyer, niche, scores)
    return {
        "status": "ok",
        "phase": "anomaly detection",
        "result": result
    }

@router.post("/api/learning/evolve-from-memory")
def learning_evolve_from_memory(payload: dict = Body(default={})):
    topic = payload.get("topic", "Faceless TikTok AI starter pack for beginners")
    buyer = payload.get("buyer", "New creators")
    niche = payload.get("niche", "Content Monetization")
    promise = payload.get("promise", "start posting quickly")
    tone = payload.get("tone", "Premium")
    bonus = payload.get("bonus", "hook templates")

    suggestion = suggest_topic_upgrade(topic, buyer, niche)
    evolved_topic = suggestion["suggested_topic"]
    evolved_buyer = suggestion["suggested_buyer"]
    evolved_niche = suggestion["suggested_niche"]

    try:
        from backend.app.money_sweep import founder_full_stack_generate
        run = founder_full_stack_generate({
            "topic": evolved_topic,
            "buyer": evolved_buyer,
            "promise": promise,
            "niche": evolved_niche,
            "tone": tone,
            "bonus": bonus,
            "notes": "learning evolve from memory"
        })
    except Exception as e:
        run = {
            "status": "fallback",
            "error": str(e),
            "content": {
                "script": (
                    f"{evolved_topic}\n\nFor: {evolved_buyer}\nPromise: {promise}\n"
                    "Hook: Start with the strongest learned angle.\n"
                    "Step 1: keep it simple.\nStep 2: keep it clear.\nStep 3: sell the outcome.\n"
                    "CTA: Use the package and execute today."
                )
            },
            "scores": {"overall": 7, "clarity": 7, "virality": 7, "monetization": 7}
        }

    scores = run.get("scores", {"overall": 7, "clarity": 7, "virality": 7, "monetization": 7})
    learned = learn_from_result(evolved_topic, evolved_buyer, evolved_niche, scores)
    anomalies = detect_anomalies(evolved_topic, evolved_buyer, evolved_niche, scores)

    manifest = {
        "time": _now(),
        "phase": "learning + anomaly detection",
        "input": {
            "topic": topic,
            "buyer": buyer,
            "niche": niche,
            "promise": promise
        },
        "evolved": {
            "topic": evolved_topic,
            "buyer": evolved_buyer,
            "niche": evolved_niche
        },
        "suggestion": suggestion,
        "run": run,
        "learned": learned,
        "anomalies": anomalies
    }

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    manifest_url = _write_output(f"{_slug(evolved_topic)}_learning_{stamp}.json", manifest)

    return {
        "status": "ok",
        "phase": "learning + anomaly detection",
        "suggestion": suggestion,
        "learned": learned,
        "anomalies": anomalies,
        "manifest_url": manifest_url,
        "run": run
    }

@router.get("/api/learning/status")
def learning_status():
    patterns = load_patterns()
    anomalies = _read_json(ANOMALIES_FILE, [])
    log = _read_json(LEARNING_LOG_FILE, [])
    return {
        "status": "ok",
        "phase": "learning status",
        "runs_learned": patterns.get("runs", 0),
        "top_winning_keywords": _top_items(patterns.get("winning_keywords", {}), 12),
        "top_losing_keywords": _top_items(patterns.get("losing_keywords", {}), 12),
        "top_winning_buyers": _top_items(patterns.get("winning_buyers", {}), 8),
        "top_winning_niches": _top_items(patterns.get("winning_niches", {}), 8),
        "recent_anomalies": (anomalies[-10:] if isinstance(anomalies, list) else []),
        "recent_learning": (log[-10:] if isinstance(log, list) else [])
    }
