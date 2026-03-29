from pathlib import Path

ALLOWED_EXTS = {".py", ".html", ".json", ".css", ".tsx", ".ts"}


def scan_repo():
    root = Path(".")
    results = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_EXTS:
            continue

        path_str = str(path).replace("\\", "/")

        if any(skip in path_str for skip in ["__pycache__", ".git", "venv", "node_modules"]):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        results.append({
            "path": path_str,
            "size": len(text),
            "lines": len(text.splitlines()),
        })

    return results
