from __future__ import annotations
import json, os, time
from typing import Dict, Any

MANUAL_SIGNAL_PATH = "backend/data/manual_interest_signals.json"

def _load(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def log_interest_signal(payload: Dict[str, Any]) -> Dict[str, Any]:
    rows = _load(MANUAL_SIGNAL_PATH)
    if not isinstance(rows, list):
        rows = []

    row = {
        "product": payload.get("product", "Unknown"),
        "source": payload.get("source", "manual"),
        "signal_type": payload.get("signal_type", "click"),
        "value": payload.get("value", 1),
        "note": payload.get("note", ""),
        "timestamp": time.time(),
    }
    rows.append(row)
    rows = rows[-200:]

    _save(MANUAL_SIGNAL_PATH, rows)
    return {"status": "ok", "logged": row, "count": len(rows)}
