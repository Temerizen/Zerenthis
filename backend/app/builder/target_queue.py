from __future__ import annotations
import json
from pathlib import Path

STATS_PATH = Path("backend/data/builder/target_stats.json")
QUEUE_STATE = Path("backend/data/builder/target_queue_state.json")

DEFAULT_TARGETS = [
    "backend/app/engines/traffic_engine.py",
    "backend/app/engines/product_engine.py",
    "backend/app/engines/offer_engine.py",
    "backend/app/engines/storefront_engine.py",
]

def _load_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _score_target(stats: dict) -> float:
    if not stats:
        return 0.0

    failures = stats.get("failures", 0)
    successes = stats.get("successes", 0)

    if successes == 0 and failures == 0:
        return 0.0

    score = successes - failures
    return score

def build_target_queue() -> list:
    stats = _load_json(STATS_PATH, {})

    targets = set(DEFAULT_TARGETS)
    targets.update(stats.keys())

    ranked = []

    for t in targets:
        s = stats.get(t, {})
        score = _score_target(s)
        ranked.append((t, score))

    ranked.sort(key=lambda x: x[1])

    return [t for t, _ in ranked]

def choose_next_target() -> dict:
    queue = build_target_queue()
    state = _load_json(QUEUE_STATE, {"last_index": -1})

    if not queue:
        return {
            "target": "backend/app/engines/traffic_engine.py",
            "reason": "fallback_no_queue"
        }

    next_index = (state.get("last_index", -1) + 1) % len(queue)
    target = queue[next_index]

    state["last_index"] = next_index
    _save_json(QUEUE_STATE, state)

    return {
        "target": target,
        "reason": "rotating_priority_queue",
        "queue": queue
    }

