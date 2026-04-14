from __future__ import annotations
import json
import time
from pathlib import Path

MEMORY_PATH = Path("backend/data/builder_memory.json")

MONEY_WEIGHTS = {
    "offer_engine.py": 1.00,
    "storefront_engine.py": 0.96,
    "traffic_engine.py": 0.92,
    "sales_engine.py": 0.95,
    "conversion_engine.py": 0.95,
    "video_engine.py": 0.78,
}

USEFULNESS_HINTS = {
    "offer": 0.20,
    "store": 0.18,
    "traffic": 0.16,
    "sales": 0.18,
    "conversion": 0.18,
    "video": 0.10,
}

def _load_memory() -> dict:
    if MEMORY_PATH.exists():
        try:
            return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save_memory(data: dict) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _base_weight(target_path: str) -> float:
    name = Path(target_path).name.lower()
    if name in MONEY_WEIGHTS:
        return MONEY_WEIGHTS[name]
    base = 0.60
    for hint, bonus in USEFULNESS_HINTS.items():
        if hint in name:
            base += bonus
    return min(base, 1.00)

def score_target(target_path: str) -> dict:
    memory = _load_memory()
    row = memory.get(target_path, {})

    wins = int(row.get("wins", 0))
    losses = int(row.get("losses", 0))
    last_touched = int(row.get("last_touched", 0))
    streak = int(row.get("streak", 0))

    base = _base_weight(target_path)
    impact = base
    money = base
    usefulness = 0.65 if "engine" in Path(target_path).name.lower() else 0.45

    success_ratio = (wins + 1) / (wins + losses + 2)
    repetition_penalty = 0.0
    if last_touched:
        age_seconds = max(0, int(time.time()) - last_touched)
        if age_seconds < 300:
            repetition_penalty = 0.20
        elif age_seconds < 1800:
            repetition_penalty = 0.10

    streak_penalty = 0.08 if streak >= 3 else 0.0

    total = (
        impact * 0.35 +
        money * 0.30 +
        usefulness * 0.15 +
        success_ratio * 0.20
    ) - repetition_penalty - streak_penalty

    total = round(total, 4)

    return {
        "target": target_path,
        "score": total,
        "impact": round(impact, 4),
        "money": round(money, 4),
        "usefulness": round(usefulness, 4),
        "success_ratio": round(success_ratio, 4),
        "repetition_penalty": round(repetition_penalty + streak_penalty, 4),
        "wins": wins,
        "losses": losses,
        "streak": streak,
    }

def choose_best_target(targets: list[str]) -> dict:
    scored = [score_target(str(t)) for t in targets if str(t).strip()]
    if not scored:
        return {"target": "", "score": 0.0}
    scored.sort(key=lambda x: x["score"], reverse=True)
    best = scored[0]
    return {
        "target": best["target"],
        "score": best["score"],
        "scored_targets": scored,
    }

def update_target_memory(target_path: str, success: bool) -> dict:
    memory = _load_memory()
    row = memory.get(target_path, {
        "wins": 0,
        "losses": 0,
        "last_touched": 0,
        "streak": 0,
        "last_result": "unknown",
    })

    if success:
        row["wins"] = int(row.get("wins", 0)) + 1
        if row.get("last_result") == "success":
            row["streak"] = int(row.get("streak", 0)) + 1
        else:
            row["streak"] = 1
        row["last_result"] = "success"
    else:
        row["losses"] = int(row.get("losses", 0)) + 1
        row["streak"] = 0
        row["last_result"] = "failure"

    row["last_touched"] = int(time.time())
    memory[target_path] = row
    _save_memory(memory)
    return row
