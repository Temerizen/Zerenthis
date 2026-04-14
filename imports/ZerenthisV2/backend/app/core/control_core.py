from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _safe_json_load(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def _safe_json_save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_") or "untitled"

def read_control_state() -> Dict[str, Any]:
    ensure_dirs()
    path = DATA_DIR / "control_state.json"
    return _safe_json_load(path, {
        "active_topic": None,
        "last_product_file": None,
        "last_offer_file": None,
        "last_traffic_file": None,
        "last_full_loop_file": None,
        "history": []
    })

def write_control_state(state: Dict[str, Any]) -> None:
    ensure_dirs()
    path = DATA_DIR / "control_state.json"
    _safe_json_save(path, state)

def append_history(event: Dict[str, Any]) -> None:
    state = read_control_state()
    history = state.get("history", [])
    history.append(event)
    state["history"] = history[-50:]
    write_control_state(state)

def set_active_topic(topic: str) -> Dict[str, Any]:
    state = read_control_state()
    state["active_topic"] = topic
    write_control_state(state)
    return state

def get_active_topic() -> Optional[str]:
    state = read_control_state()
    topic = state.get("active_topic")
    if isinstance(topic, str) and topic.strip():
        return topic.strip()
    return None

def try_extract_topic_from_leaderboard() -> Optional[str]:
    leaderboard = DATA_DIR / "leaderboard.json"
    data = _safe_json_load(leaderboard, [])
    if isinstance(data, list) and data:
        top = data[0]
        if isinstance(top, dict):
            for key in ("topic", "title", "winner", "name"):
                value = top.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    return None

def try_extract_topic_from_output_files() -> Optional[str]:
    candidates: List[Path] = []
    candidates.extend(sorted(OUTPUT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True))
    candidates.extend(sorted(OUTPUT_DIR.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True))
    for path in candidates[:12]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
            if not text:
                continue
            if path.suffix.lower() == ".json":
                obj = json.loads(text)
                if isinstance(obj, dict):
                    for key in ("topic", "title", "winner_topic", "active_topic"):
                        value = obj.get(key)
                        if isinstance(value, str) and value.strip():
                            return value.strip()
            else:
                first = text.splitlines()[0].strip()
                if 6 <= len(first) <= 180:
                    return first
        except Exception:
            continue
    return None

def resolve_topic(explicit_topic: Optional[str] = None) -> str:
    if isinstance(explicit_topic, str) and explicit_topic.strip():
        topic = explicit_topic.strip()
        set_active_topic(topic)
        append_history({"event": "topic_set", "topic": topic})
        return topic

    active = get_active_topic()
    if active:
        return active

    inferred = try_extract_topic_from_leaderboard() or try_extract_topic_from_output_files()
    if inferred:
        set_active_topic(inferred)
        append_history({"event": "topic_inferred", "topic": inferred})
        return inferred

    fallback = "AI productivity system for overwhelmed creators"
    set_active_topic(fallback)
    append_history({"event": "topic_fallback", "topic": fallback})
    return fallback
