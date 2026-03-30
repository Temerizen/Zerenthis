from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def _safe_read(path: Path, limit: int = 5000) -> str:
    try:
        if not path.exists() or not path.is_file():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

def analyze_system():
    targets = [
        ROOT / "backend" / "app" / "main.py",
        ROOT / "backend" / "Engine" / "product_engine.py",
        ROOT / "backend" / "Engine" / "video_engine.py",
        ROOT / "backend" / "self_improver" / "routes.py",
        ROOT / "index.html",
    ]

    chunks = []
    for t in targets:
        if t.exists():
            chunks.append(f"FILE: {t.relative_to(ROOT)}\n{_safe_read(t)}")
    text = "\n\n".join(chunks)

    ideas = []

    if "recent_outputs" not in text and '@app.get("/health")' in text:
        ideas.append({
            "title": "Add recent output visibility to health",
            "reason": "This improves operator visibility and gives the system better awareness of recent assets.",
            "steps": [
                {
                    "action": "edit_file",
                    "path": "backend/app/main.py",
                    "find": '@app.get("/health")\ndef health():\n    return {\n        "ok": True,\n        "service": "Zerenthis Automation Core",\n        "outputs_dir": str(OUTPUT_DIR),\n        "outputs_exists": OUTPUT_DIR.exists(),\n    }\n',
                    "replace": '@app.get("/health")\ndef health():\n    files = [p for p in OUTPUT_DIR.iterdir() if p.is_file()]\n    recent = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]\n    return {\n        "ok": True,\n        "service": "Zerenthis Automation Core",\n        "outputs_dir": str(OUTPUT_DIR),\n        "outputs_exists": OUTPUT_DIR.exists(),\n        "recent_outputs": [p.name for p in recent],\n    }\n',
                }
            ],
        })

    if 'Approval rate' not in text and 'Founder Panel' in text:
        ideas.append({
            "title": "Add guided founder copy",
            "reason": "A tiny UI improvement makes the system feel more magical and directed.",
            "steps": [
                {
                    "action": "edit_file",
                    "path": "index.html",
                    "find": '<div class="sub">Generate assets, review proposals, and monitor applied or failed changes.</div>',
                    "replace": '<div class="sub">Generate assets, review proposals, and monitor applied or failed changes.</div><div class="sub">Magic mode is active: low-risk improvements can self-heal, while bigger changes wait for your judgment.</div>',
                }
            ],
        })

    return ideas[:1]
