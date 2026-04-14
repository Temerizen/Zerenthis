from __future__ import annotations
import json
from pathlib import Path

VARIANT_PATH = Path("backend/data/variant_battle.json")

def get_variant_winner() -> dict:
    if not VARIANT_PATH.exists():
        return {}

    try:
        data = json.loads(VARIANT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    winner = data.get("winner", {})
    return winner if isinstance(winner, dict) else {}
