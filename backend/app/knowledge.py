from fastapi import APIRouter, Body
from pathlib import Path
from datetime import datetime, timezone
import json, uuid, math, re

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
KNOW_DIR = DATA_DIR / "knowledge"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
KNOW_DIR.mkdir(parents=True, exist_ok=True)

PACKS_FILE = KNOW_DIR / "packs.json"
MEMORY_FILE = KNOW_DIR / "memory.json"
RANKINGS_FILE = KNOW_DIR / "rankings.json"

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
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "knowledge")).strip("_")[:80] or "knowledge"

def _load_packs():
    data = _read_json(PACKS_FILE, {"packs": []})
    if not isinstance(data, dict):
        data = {"packs": []}
    data.setdefault("packs", [])
    return data

def _save_packs(data: dict):
    _write_json(PACKS_FILE, data)

def _load_memory():
    data = _read_json(MEMORY_FILE, {"items": []})
    if not isinstance(data, dict):
        data = {"items": []}
    data.setdefault("items", [])
    return data

def _save_memory(data: dict):
    _write_json(MEMORY_FILE, data)

def _load_rankings():
    data = _read_json(RANKINGS_FILE, {"history": []})
    if not isinstance(data, dict):
        data = {"history": []}
    data.setdefault("history", [])
    return data

def _save_rankings(data: dict):
    _write_json(RANKINGS_FILE, data)

def _write_output(name: str, data: dict):
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

def _tokenize(text: str):
    raw = (text or "").lower().replace("-", " ").replace("/", " ")
    parts = re.findall(r"[a-z0-9]+", raw)
    return [p for p in parts if len(p) >= 3][:80]

def _jaccard(a_tokens, b_tokens):
    a = set(a_tokens or [])
    b = set(b_tokens or [])
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))

def _hours_ago(iso_time: str):
    try:
        dt = datetime.fromisoformat((iso_time or "").replace("Z", "+00:00"))
        return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0)
    except Exception:
        return 999999.0

def _recency_score(iso_time: str):
    h = _hours_ago(iso_time)
    return 1.0 / (1.0 + (h / 72.0))

def _importance_score(item: dict):
    base = float(item.get("importance", 5))
    profit = float(item.get("profitability", 5))
    confidence = float(item.get("confidence", 5))
    return ((base * 0.45) + (profit * 0.35) + (confidence * 0.20)) / 10.0

def _pack_match_score(item: dict, packs: list):
    item_niche = (item.get("niche") or "").strip().lower()
    item_buyer = (item.get("buyer") or "").strip().lower()
    score = 0.0
    for pack in packs or []:
        niche = (pack.get("niche") or "").strip().lower()
        buyer = (pack.get("buyer") or "").strip().lower()
        if niche and item_niche and niche == item_niche:
            score += 0.18
        if buyer and item_buyer and buyer == item_buyer:
            score += 0.12
        for kw in pack.get("keywords", []) or []:
            if kw in (item.get("tokens") or []):
                score += 0.03
    return min(score, 0.35)

def _rank_item(query: str, item: dict, packs: list):
    q_tokens = _tokenize(query)
    i_tokens = item.get("tokens") or _tokenize(item.get("text", ""))
    similarity = _jaccard(q_tokens, i_tokens)
    recency = _recency_score(item.get("created_at", ""))
    importance = _importance_score(item)
    pack_fit = _pack_match_score(item, packs)

    final = round(
        (similarity * 0.42) +
        (recency * 0.18) +
        (importance * 0.25) +
        (pack_fit * 0.15),
        4
    )

    return {
        "similarity": round(similarity, 4),
        "recency": round(recency, 4),
        "importance": round(importance, 4),
        "pack_fit": round(pack_fit, 4),
        "final": final
    }

def _default_pack_template(name: str, niche: str, buyer: str):
    return {
        "id": f"pack_{uuid.uuid4().hex[:10]}",
        "name": name or "Untitled Pack",
        "niche": niche or "Content Monetization",
        "buyer": buyer or "Creators",
        "keywords": [],
        "principles": [],
        "offers": [],
        "hooks": [],
        "risks": [],
        "created_at": _now(),
        "updated_at": _now()
    }

def _append_ranking_history(entry: dict):
    data = _load_rankings()
    data["history"].append(entry)
    data["history"] = data["history"][-300:]
    _save_rankings(data)

@router.post("/api/knowledge/pack/create")
def knowledge_pack_create(payload: dict = Body(...)):
    packs = _load_packs()
    pack = _default_pack_template(
        payload.get("name", "Untitled Pack"),
        payload.get("niche", "Content Monetization"),
        payload.get("buyer", "Creators")
    )
    pack["keywords"] = payload.get("keywords", []) or []
    pack["principles"] = payload.get("principles", []) or []
    pack["offers"] = payload.get("offers", []) or []
    pack["hooks"] = payload.get("hooks", []) or []
    pack["risks"] = payload.get("risks", []) or []

    packs["packs"].append(pack)
    packs["packs"] = packs["packs"][-200:]
    _save_packs(packs)

    return {
        "status": "ok",
        "phase": "knowledge packs + memory ranking",
        "pack": pack
    }

@router.post("/api/knowledge/pack/ingest")
def knowledge_pack_ingest(payload: dict = Body(...)):
    name = payload.get("name", "Generated Knowledge Pack")
    niche = payload.get("niche", "Content Monetization")
    buyer = payload.get("buyer", "Creators")
    source_text = payload.get("text", "")

    packs = _load_packs()
    pack = _default_pack_template(name, niche, buyer)

    tokens = _tokenize(source_text)
    pack["keywords"] = sorted(list(dict.fromkeys(tokens[:20])))
    pack["principles"] = [
        "Keep the promise clear",
        "Reduce friction to execution",
        "Prioritize monetizable outcomes",
        "Repeat strong angles and cut weak ones"
    ]
    pack["offers"] = [
        f"{niche} starter offer",
        f"{niche} premium offer",
        f"{niche} authority offer"
    ]
    pack["hooks"] = [
        f"How {buyer} can win in {niche}",
        f"The simplest {niche} shortcut most people miss",
        f"Use this {niche} workflow before everyone catches on"
    ]
    pack["risks"] = [
        "weak differentiation",
        "blurry promise",
        "low monetization angle"
    ]

    packs["packs"].append(pack)
    packs["packs"] = packs["packs"][-200:]
    _save_packs(packs)

    artifact_url = _write_output(
        f"{_slug(pack['name'])}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_pack.json",
        pack
    )

    return {
        "status": "ok",
        "phase": "knowledge packs + memory ranking",
        "pack": pack,
        "artifact_url": artifact_url
    }

@router.post("/api/knowledge/memory/add")
def knowledge_memory_add(payload: dict = Body(...)):
    memory = _load_memory()
    text = payload.get("text", "")
    item = {
        "id": f"mem_{uuid.uuid4().hex[:10]}",
        "text": text,
        "tokens": _tokenize(text),
        "topic": payload.get("topic", ""),
        "niche": payload.get("niche", "Content Monetization"),
        "buyer": payload.get("buyer", "Creators"),
        "importance": float(payload.get("importance", 5)),
        "profitability": float(payload.get("profitability", 5)),
        "confidence": float(payload.get("confidence", 5)),
        "source": payload.get("source", "manual"),
        "created_at": _now()
    }
    memory["items"].append(item)
    memory["items"] = memory["items"][-1000:]
    _save_memory(memory)

    return {
        "status": "ok",
        "phase": "knowledge packs + memory ranking",
        "memory_item": item
    }

@router.post("/api/knowledge/memory/rank")
def knowledge_memory_rank(payload: dict = Body(...)):
    query = payload.get("query", "")
    pack_names = set([str(x).strip().lower() for x in (payload.get("pack_names", []) or [])])

    packs = _load_packs().get("packs", [])
    if pack_names:
        packs = [p for p in packs if (p.get("name", "") or "").strip().lower() in pack_names]

    items = _load_memory().get("items", [])
    ranked = []
    for item in items:
        score = _rank_item(query, item, packs)
        ranked.append({
            "item": item,
            "score": score
        })

    ranked = sorted(ranked, key=lambda x: x["score"]["final"], reverse=True)[:20]

    history_entry = {
        "time": _now(),
        "query": query,
        "pack_names": list(pack_names),
        "top_results": [
            {
                "id": r["item"]["id"],
                "topic": r["item"].get("topic", ""),
                "final": r["score"]["final"]
            } for r in ranked[:10]
        ]
    }
    _append_ranking_history(history_entry)

    return {
        "status": "ok",
        "phase": "knowledge packs + memory ranking",
        "query": query,
        "results": ranked
    }

@router.post("/api/knowledge/apply")
def knowledge_apply(payload: dict = Body(...)):
    query = payload.get("query", "")
    topic = payload.get("topic", "Knowledge Guided Topic")
    buyer = payload.get("buyer", "Creators")
    niche = payload.get("niche", "Content Monetization")
    promise = payload.get("promise", "move faster")

    packs = _load_packs().get("packs", [])
    items = _load_memory().get("items", [])

    ranked = []
    for item in items:
        score = _rank_item(query or topic, item, packs)
        ranked.append({"item": item, "score": score})
    ranked = sorted(ranked, key=lambda x: x["score"]["final"], reverse=True)[:8]

    best_pack = None
    if packs:
        best_pack = sorted(
            packs,
            key=lambda p: sum(1 for kw in (p.get("keywords") or []) if kw in _tokenize(query or topic)),
            reverse=True
        )[0]

    memory_text = "\n".join([
        f"- {r['item'].get('text','')[:220]}"
        for r in ranked[:5]
    ])

    guided_topic = topic
    if best_pack and best_pack.get("keywords"):
        bonus_kw = next((kw for kw in best_pack["keywords"] if kw not in _tokenize(topic)), "")
        if bonus_kw:
            guided_topic = f"{topic} {bonus_kw}".strip()

    guidance = {
        "guided_topic": guided_topic,
        "buyer": buyer,
        "niche": niche,
        "promise": promise,
        "pack": best_pack,
        "memory_context": memory_text
    }

    try:
        from backend.app.money_sweep import founder_full_stack_generate
        run = founder_full_stack_generate({
            "topic": guided_topic,
            "buyer": buyer,
            "promise": promise,
            "niche": niche,
            "tone": "Premium",
            "bonus": "knowledge-pack advantage",
            "notes": f"knowledge-guided run\n\nPack + memory context:\n{memory_text[:1200]}"
        })
    except Exception as e:
        run = {
            "status": "fallback",
            "error": str(e),
            "content": {
                "script": (
                    f"{guided_topic}\n\nFor: {buyer}\nPromise: {promise}\nNiche: {niche}\n\n"
                    f"Knowledge context:\n{memory_text[:800]}\n\n"
                    "Step 1: use the strongest memory pattern.\n"
                    "Step 2: keep the promise clean.\n"
                    "Step 3: package the monetizable result.\n"
                    "CTA: execute the strongest version now."
                )
            }
        }

    artifact = {
        "time": _now(),
        "phase": "knowledge packs + memory ranking",
        "query": query,
        "guidance": guidance,
        "ranked_memory": ranked,
        "run": run
    }

    artifact_url = _write_output(
        f"{_slug(guided_topic)}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_knowledge_apply.json",
        artifact
    )

    return {
        "status": "ok",
        "phase": "knowledge packs + memory ranking",
        "guidance": guidance,
        "artifact_url": artifact_url,
        "run": run
    }

@router.get("/api/knowledge/status")
def knowledge_status():
    packs = _load_packs().get("packs", [])
    memory = _load_memory().get("items", [])
    rankings = _load_rankings().get("history", [])

    recent_memory = sorted(memory, key=lambda x: x.get("created_at", ""), reverse=True)[:12]
    recent_packs = sorted(packs, key=lambda x: x.get("updated_at", x.get("created_at", "")), reverse=True)[:12]
    recent_rankings = sorted(rankings, key=lambda x: x.get("time", ""), reverse=True)[:12]

    return {
        "status": "ok",
        "phase": "knowledge packs + memory ranking",
        "counts": {
            "packs": len(packs),
            "memory_items": len(memory),
            "ranking_history": len(rankings)
        },
        "recent_packs": recent_packs,
        "recent_memory": recent_memory,
        "recent_rankings": recent_rankings
    }
