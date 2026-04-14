import json, os, time

VAL_PATH = "backend/data/validation_feedback.json"
EXEC_PATH = "backend/data/execution_loop.json"
MEM_PATH = "backend/data/memory_depth.json"
STAB_PATH = "backend/data/stability.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"__load_error__": str(e)}

def _safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _normalize_validation_store(val):
    if not isinstance(val, dict):
        return {"last_validation": None, "history": []}

    if "last_validation" not in val:
        val["last_validation"] = None

    if "history" not in val or not isinstance(val["history"], list):
        val["history"] = []

    return val

def run():
    val = _normalize_validation_store(
        _safe_load(VAL_PATH, {"last_validation": None, "history": []})
    )

    memory = _safe_load(MEM_PATH, {})
    stability = _safe_load(STAB_PATH, {})

    exec_data = _safe_load(EXEC_PATH, {"last_execution": None})
    execution = exec_data.get("last_execution") if isinstance(exec_data, dict) else None

    if not execution:
        record = {
            "timestamp": time.time(),
            "status": "no_execution_to_validate",
            "exec_path_exists": os.path.exists(EXEC_PATH),
            "exec_data_preview": exec_data if isinstance(exec_data, dict) else str(type(exec_data))
        }
        val["last_validation"] = record
        val["history"].append(record)
        val["history"] = val["history"][-50:]
        _safe_save(VAL_PATH, val)
        return {
            "status": "validated",
            "validation": record
        }

    trend = memory.get("trend", "unknown")

    baseline = {}
    if isinstance(stability, dict):
        baseline = stability.get("last_baseline") or stability.get("baseline") or {}

    overall_score = baseline.get("overall_score", 0.5)

    if trend in ["improving", "stable_positive"] and overall_score >= 0.65:
        result = "improved"
        decision = "reinforce"
    elif trend in ["declining", "unstable"] and overall_score < 0.65:
        result = "not_improved"
        decision = "reject"
    else:
        result = "inconclusive"
        decision = "observe"

    record = {
        "timestamp": time.time(),
        "status": "validated",
        "execution_component": execution.get("component"),
        "target_file": execution.get("target_file"),
        "trend": trend,
        "overall_score": overall_score,
        "result": result,
        "decision": decision
    }

    val["last_validation"] = record
    val["history"].append(record)
    val["history"] = val["history"][-50:]
    _safe_save(VAL_PATH, val)

    return {
        "status": "validated",
        "validation": record
    }
