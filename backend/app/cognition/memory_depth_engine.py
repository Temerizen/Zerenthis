import json, os, time

MEM_PATH = "backend/data/memory_depth.json"
REALITY_PATH = "backend/data/reality.json"

MAX_HISTORY = 20

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def _safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _detect_trend(scores):
    if len(scores) < 3:
        return "insufficient_data"

    if scores[-1] > scores[-2] > scores[-3]:
        return "improving"
    elif scores[-1] < scores[-2] < scores[-3]:
        return "declining"
    else:
        return "unstable"

def run():
    memory = _safe_load(MEM_PATH, {
        "recent_scores": [],
        "trend": None,
        "last_pattern": None
    })

    reality = _safe_load(REALITY_PATH, {"last_outcome": None})
    last_outcome = reality.get("last_outcome")

    if not last_outcome:
        return {"status": "no_memory_update"}

    score = float(last_outcome.get("score", 0.5))

    memory["recent_scores"].append(score)
    memory["recent_scores"] = memory["recent_scores"][-MAX_HISTORY:]

    trend = _detect_trend(memory["recent_scores"])

    memory["trend"] = trend
    memory["last_pattern"] = {
        "timestamp": time.time(),
        "trend": trend,
        "latest_score": round(score, 4)
    }

    _safe_save(MEM_PATH, memory)

    return {
        "status": "memory_updated",
        "trend": trend,
        "score": score
    }
