from fastapi import APIRouter, Body, UploadFile, File
from pathlib import Path
from datetime import datetime, timezone
import os, json, base64, uuid

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
SESSION_DIR = DATA_DIR / "live_sessions"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DIR.mkdir(parents=True, exist_ok=True)

def _now():
    return datetime.now(timezone.utc).isoformat()

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "live")).strip("_")[:80] or "live"

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

def _write_output_json(name: str, data: dict) -> str:
    path = OUTPUT_DIR / name
    _write_json(path, data)
    return f"/api/file/{name}"

def _write_output_text(name: str, text: str) -> str:
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return f"/api/file/{name}"

def _session_path(session_id: str) -> Path:
    return SESSION_DIR / f"{session_id}.json"

def _new_session(mode: str = "live"):
    session_id = f"live_{uuid.uuid4().hex[:12]}"
    data = {
        "session_id": session_id,
        "mode": mode,
        "created_at": _now(),
        "updated_at": _now(),
        "messages": [],
        "files": [],
        "state": {
            "topic": "",
            "buyer": "",
            "promise": "",
            "niche": "",
            "intent": "general"
        }
    }
    _write_json(_session_path(session_id), data)
    return data

def _load_session(session_id: str):
    return _read_json(_session_path(session_id), None)

def _save_session(data: dict):
    data["updated_at"] = _now()
    _write_json(_session_path(data["session_id"]), data)

def _append_message(data: dict, role: str, kind: str, content: dict):
    data["messages"].append({
        "time": _now(),
        "role": role,
        "kind": kind,
        "content": content
    })
    data["messages"] = data["messages"][-200:]
    _save_session(data)

def _save_uploaded_bytes(filename: str, raw: bytes) -> Path:
    name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
    path = UPLOAD_DIR / name
    with open(path, "wb") as f:
        f.write(raw)
    return path

def _basic_text_intel(text: str):
    t = (text or "").lower()
    niche = "Content Monetization"
    buyer = "Creators"
    promise = "move faster"
    intent = "general"

    if any(x in t for x in ["fitness", "workout", "gym"]):
        niche = "Fitness"
    elif any(x in t for x in ["crypto", "trading", "finance", "stock"]):
        niche = "Finance"
    elif any(x in t for x in ["ai", "automation", "agent", "tech"]):
        niche = "AI / Tech"

    if any(x in t for x in ["founder", "business", "agency"]):
        buyer = "Founders"

    if any(x in t for x in ["money", "sell", "offer", "income", "revenue"]):
        promise = "make money faster"
        intent = "monetization"
    elif any(x in t for x in ["content", "post", "youtube", "tiktok"]):
        promise = "create content faster"
        intent = "content"

    return {
        "niche": niche,
        "buyer": buyer,
        "promise": promise,
        "intent": intent
    }

def _basic_visual_intel(filename: str):
    name = (filename or "").lower()
    tags = ["screen", "text", "visual"]
    niche = "Content Monetization"

    if "fitness" in name:
        niche = "Fitness"
        tags.append("fitness")
    elif "crypto" in name or "stock" in name:
        niche = "Finance"
        tags.append("finance")
    elif "ai" in name or "tech" in name:
        niche = "AI / Tech"
        tags.append("tech")

    return {
        "niche": niche,
        "tags": tags,
        "angles": [
            "step-by-step breakdown",
            "mistakes to avoid",
            "before and after transformation",
            "simple monetization angle"
        ]
    }

def _merge_state(existing: dict, text_intel: dict | None = None, visual_intel: dict | None = None):
    state = dict(existing or {})
    ti = text_intel or {}
    vi = visual_intel or {}

    if not state.get("niche") and ti.get("niche"):
        state["niche"] = ti["niche"]
    if not state.get("buyer") and ti.get("buyer"):
        state["buyer"] = ti["buyer"]
    if not state.get("promise") and ti.get("promise"):
        state["promise"] = ti["promise"]
    if ti.get("intent"):
        state["intent"] = ti["intent"]

    if vi.get("niche"):
        state["niche"] = vi["niche"] if state.get("niche") in ("", "general") else state["niche"]

    if not state.get("topic"):
        state["topic"] = f"{state.get('niche', 'AI')} live strategy"

    if not state.get("buyer"):
        state["buyer"] = "Creators"
    if not state.get("promise"):
        state["promise"] = "move faster"
    if not state.get("niche"):
        state["niche"] = "Content Monetization"
    if not state.get("intent"):
        state["intent"] = "general"

    return state

def _build_live_response(state: dict, transcript: str, visual_notes: list):
    topic = state.get("topic", "AI live strategy")
    buyer = state.get("buyer", "Creators")
    promise = state.get("promise", "move faster")
    niche = state.get("niche", "Content Monetization")
    intent = state.get("intent", "general")

    hooks = [
        f"How {buyer} can use {topic} to {promise}",
        f"The easiest {niche} angle most people miss",
        f"Use this {topic} workflow before everyone catches on"
    ]

    script = (
        f"{topic}\n\n"
        f"For: {buyer}\n"
        f"Promise: {promise}\n"
        f"Niche: {niche}\n"
        f"Intent: {intent}\n\n"
        f"Transcript signals: {transcript[:280] if transcript else 'none'}\n"
        f"Visual signals: {', '.join(visual_notes[:6]) if visual_notes else 'none'}\n\n"
        "Step 1: identify the strongest angle.\n"
        "Step 2: turn it into one clear asset.\n"
        "Step 3: attach a direct execution path.\n"
        "CTA: execute the best version today."
    )

    cta = f"Use the {topic} package and start to {promise}."

    return {
        "topic": topic,
        "buyer": buyer,
        "promise": promise,
        "niche": niche,
        "intent": intent,
        "hooks": hooks,
        "script": script,
        "cta": cta
    }

@router.post("/api/live/start")
def live_start(payload: dict = Body(default={})):
    mode = payload.get("mode", "live")
    session = _new_session(mode=mode)
    return {
        "status": "ok",
        "phase": "live multimodal mode",
        "session_id": session["session_id"],
        "session": session
    }

@router.post("/api/live/message")
def live_message(payload: dict = Body(...)):
    session_id = payload.get("session_id", "")
    text = payload.get("text", "")
    topic = payload.get("topic", "")

    session = _load_session(session_id)
    if not session:
        return {"status": "error", "error": "session not found"}

    text_intel = _basic_text_intel(text)
    if topic:
        session["state"]["topic"] = topic

    session["state"] = _merge_state(session.get("state", {}), text_intel=text_intel)
    _append_message(session, "user", "text", {"text": text})

    visual_notes = []
    for f in session.get("files", [])[-6:]:
        for tag in (f.get("analysis", {}) or {}).get("tags", []):
            if tag not in visual_notes:
                visual_notes.append(tag)

    response = _build_live_response(session["state"], text, visual_notes)
    _append_message(session, "assistant", "live_response", response)

    return {
        "status": "ok",
        "phase": "live multimodal mode",
        "session_id": session_id,
        "response": response,
        "state": session["state"]
    }

@router.post("/api/live/upload")
async def live_upload(session_id: str, file: UploadFile = File(...)):
    session = _load_session(session_id)
    if not session:
        return {"status": "error", "error": "session not found"}

    raw = await file.read()
    path = _save_uploaded_bytes(file.filename, raw)
    analysis = _basic_visual_intel(path.name)

    file_entry = {
        "time": _now(),
        "name": path.name,
        "size": len(raw),
        "analysis": analysis
    }
    session["files"].append(file_entry)
    session["files"] = session["files"][-50:]
    session["state"] = _merge_state(session.get("state", {}), visual_intel=analysis)
    _save_session(session)

    _append_message(session, "user", "file", {"name": path.name, "analysis": analysis})

    return {
        "status": "ok",
        "phase": "live multimodal mode",
        "session_id": session_id,
        "file": file_entry,
        "state": session["state"]
    }

@router.post("/api/live/upload-base64")
def live_upload_base64(payload: dict = Body(...)):
    session_id = payload.get("session_id", "")
    filename = payload.get("filename", f"live_{uuid.uuid4().hex[:6]}.png")
    image_base64 = payload.get("image_base64", "")

    session = _load_session(session_id)
    if not session:
        return {"status": "error", "error": "session not found"}

    try:
        raw = base64.b64decode(image_base64)
    except Exception as e:
        return {"status": "error", "error": str(e)}

    path = _save_uploaded_bytes(filename, raw)
    analysis = _basic_visual_intel(path.name)

    file_entry = {
        "time": _now(),
        "name": path.name,
        "size": len(raw),
        "analysis": analysis
    }
    session["files"].append(file_entry)
    session["files"] = session["files"][-50:]
    session["state"] = _merge_state(session.get("state", {}), visual_intel=analysis)
    _save_session(session)

    _append_message(session, "user", "file", {"name": path.name, "analysis": analysis})

    return {
        "status": "ok",
        "phase": "live multimodal mode",
        "session_id": session_id,
        "file": file_entry,
        "state": session["state"]
    }

@router.post("/api/live/generate")
def live_generate(payload: dict = Body(...)):
    session_id = payload.get("session_id", "")
    session = _load_session(session_id)
    if not session:
        return {"status": "error", "error": "session not found"}

    transcript_parts = []
    visual_notes = []
    for m in session.get("messages", []):
        if m.get("kind") == "text":
            transcript_parts.append((m.get("content") or {}).get("text", ""))
    for f in session.get("files", []):
        for tag in (f.get("analysis", {}) or {}).get("tags", []):
            if tag not in visual_notes:
                visual_notes.append(tag)

    transcript = " | ".join([x for x in transcript_parts if x])[:1200]
    response = _build_live_response(session.get("state", {}), transcript, visual_notes)

    try:
        from backend.app.money_sweep import founder_full_stack_generate
        run = founder_full_stack_generate({
            "topic": response["topic"],
            "buyer": response["buyer"],
            "promise": response["promise"],
            "niche": response["niche"],
            "tone": "Premium",
            "bonus": "live multimodal hooks",
            "notes": "live multimodal generation"
        })
    except Exception as e:
        run = {
            "status": "fallback",
            "error": str(e),
            "content": {
                "script": response["script"],
                "hooks": response["hooks"],
                "cta": response["cta"]
            }
        }

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem = f"{_slug(response['topic'])}_live_{stamp}"
    manifest = {
        "time": _now(),
        "phase": "live multimodal mode",
        "session_id": session_id,
        "state": session.get("state", {}),
        "response": response,
        "run": run,
        "message_count": len(session.get("messages", [])),
        "file_count": len(session.get("files", []))
    }
    manifest_url = _write_output_json(f"{stem}_manifest.json", manifest)
    brief_url = _write_output_text(f"{stem}_brief.txt", response["script"])

    _append_message(session, "assistant", "generation", {
        "manifest_url": manifest_url,
        "brief_url": brief_url,
        "topic": response["topic"]
    })

    return {
        "status": "ok",
        "phase": "live multimodal mode",
        "session_id": session_id,
        "manifest_url": manifest_url,
        "brief_url": brief_url,
        "response": response,
        "run": run
    }

@router.get("/api/live/session/{session_id}")
def live_session(session_id: str):
    session = _load_session(session_id)
    if not session:
        return {"status": "error", "error": "session not found"}
    return {
        "status": "ok",
        "phase": "live multimodal mode",
        "session": session
    }
