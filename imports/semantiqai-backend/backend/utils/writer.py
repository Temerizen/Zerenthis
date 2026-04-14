from pathlib import Path
from backend.utils.files import ensure_parent

def write_text_file(path: Path, content: str) -> str:
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")
    return str(path)

def append_text_file(path: Path, content: str) -> str:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as f:
        f.write(content)
    return str(path)
