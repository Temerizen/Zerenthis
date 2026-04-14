from typing import List, Dict, Any
import json
from pathlib import Path
from backend.core.config import MEMORY_DIR

MEMORY_FILE = Path(MEMORY_DIR) / "short_term_memory.json"

def _read_memory() -> List[Dict[str, Any]]:
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def _write_memory(items: List[Dict[str, Any]]) -> None:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(items[-100:], indent=2), encoding="utf-8")

def remember(role: str, content: str, category: str = "general") -> None:
    items = _read_memory()
    items.append({
        "role": role,
        "content": content,
        "category": category
    })
    _write_memory(items)

def recall(limit: int = 10, category: str | None = None) -> List[Dict[str, Any]]:
    items = _read_memory()
    if category:
        items = [x for x in items if x.get("category") == category]
    return items[-limit:]

def clear_memory() -> None:
    _write_memory([])

