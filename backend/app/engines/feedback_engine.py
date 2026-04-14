from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parents[2]
FEEDBACK_DIR = BASE_DIR / "data" / "feedback"
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

def log_feedback(entry: Dict[str, Any]) -> Dict[str, Any]:
    ts = datetime.utcnow().strftime("%Y%m%d")
    out = FEEDBACK_DIR / f"feedback_{ts}.jsonl"
    entry = dict(entry)
    entry["logged_at"] = datetime.utcnow().isoformat()
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"ok": True, "file": str(out).replace("\\", "/")}

