from datetime import datetime
from pathlib import Path
import re

def slugify(value: str) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "untitled"

def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
