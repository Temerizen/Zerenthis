import json, os, time

REFLECT_PATH = "backend/data/self_reflection.json"
IDENTITY_PATH = "backend/data/identity_consolidation.json"
IDENTITY_MEMORY_PATH = "backend/data/identity_memory.json"
STABILITY_PATH = "backend/data/stability.json"
VALIDATION_PATH = "backend/data/validation_feedback.json"
REINFORCEMENT_PATH = "backend/data/reinforcement.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return default

def _safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run():
    reflection = _safe_load(REFLECT_PATH, {"last_reflection": None, "history": []})
    identity = _safe_load(IDENTITY_PATH, {"traits": {}, "last_identity_update": None, "history": []})
    identity_memory = _safe_load(IDENTITY_MEMORY_PATH, {"baseline_traits": {}, "history": []})
    stability = _safe_load(STABILITY_PATH, {"last_baseline": None, "history": []})
    validation = _safe_load(VALIDATION_PATH, {"last_validation": None, "history": []})
    reinforcement = _safe_load(REINFORCEMENT_PATH, {"weights": {}, "history": []})

    traits = identity.get("traits", {})
    baseline_traits = identity_memory.get("baseline_traits", {})
    baseline = stability.get("last_baseline") or {}
    canonical = baseline.get("canonical") or {}
    flags = baseline.get("flags") or {}
    last_validation = validation.get("last_validation") or {}
    weights = reinforcement.get("weights", {})

    score = canonical.get("last_score", 0.5)
    mission_progress = canonical.get("mission_progress", 0.0)
    strategy = canonical.get("strategy", "default")
    coherent = flags.get("coherent", False)
    decision = last_validation.get("decision", "observe")
    result = last_validation.get("result", "inconclusive")
    mr_weight = weights.get("memory_reasoning", 0.5)

    confidence = traits.get("confidence", 0.5)
    persistence = traits.get("persistence", 0.5)
    caution = traits.get("caution", 0.5)
    adaptability = traits.get("adaptability", 0.5)

    reflections = []

    if coherent:
        reflections.append("System state is aligned.")
    else:
        reflections.append("System state is misaligned and needs correction.")

    if mission_progress >= 0.9:
        reflections.append("Mission is close to completion.")
    elif mission_progress >= 0.5:
        reflections.append("Mission is progressing steadily.")
    else:
        reflections.append("Mission is still in an early or mid phase.")

    if result == "improved":
        reflections.append("Recent change appears beneficial.")
    elif result == "not_improved":
        reflections.append("Recent change appears ineffective.")
    else:
        reflections.append("Recent change remains uncertain and should be observed.")

    if confidence > 0.6 and persistence > 0.6:
        reflections.append("Identity is becoming more confident and persistent.")
    elif confidence > 0.55:
        reflections.append("Confidence is increasing gradually.")
    else:
        reflections.append("Identity is still forming with moderate confidence.")

    if mr_weight > 0.6:
        reflections.append("Memory-reasoning pathway is gaining trust.")
    elif mr_weight > 0.5:
        reflections.append("Memory-reasoning pathway is being cautiously reinforced.")
    else:
        reflections.append("Memory-reasoning pathway is not yet strongly trusted.")

    narrative = " ".join(reflections)

    record = {
        "timestamp": time.time(),
        "summary": narrative,
        "state": {
            "score": round(float(score), 4),
            "mission_progress": round(float(mission_progress), 4),
            "strategy": strategy,
            "coherent": bool(coherent),
            "validation_result": result,
            "validation_decision": decision,
            "memory_reasoning_weight": round(float(mr_weight), 4)
        },
        "traits": {
            "caution": round(float(caution), 4),
            "adaptability": round(float(adaptability), 4),
            "confidence": round(float(confidence), 4),
            "persistence": round(float(persistence), 4)
        },
        "baseline_traits": {
            "caution": round(float(baseline_traits.get("caution", 0.5)), 4),
            "adaptability": round(float(baseline_traits.get("adaptability", 0.5)), 4),
            "confidence": round(float(baseline_traits.get("confidence", 0.5)), 4),
            "persistence": round(float(baseline_traits.get("persistence", 0.5)), 4)
        }
    }

    reflection["last_reflection"] = record
    reflection["history"].append(record)
    reflection["history"] = reflection["history"][-100:]

    _safe_save(REFLECT_PATH, reflection)

    return {
        "status": "self_reflection_complete",
        "reflection": record
    }
