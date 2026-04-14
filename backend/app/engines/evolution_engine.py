import os, json, random

DATA_DIR = "backend/data"

def safe_load(path, default=None):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def mutate_topic(topic):
    mutations = [
        topic + "_system",
        topic + "_blueprint",
        topic + "_method",
        topic + "_hack",
        topic + "_formula"
    ]
    return random.choice(mutations)

def run():
    perf_log = safe_load(os.path.join(DATA_DIR, "performance_log.json"), [])
    current = safe_load(os.path.join(DATA_DIR, "current_topic.json"), {"topic": "unknown_topic"})

    topic = current.get("topic")

    if not perf_log:
        return {"status": "no_data"}

    last = perf_log[-1]
    should_scale = last.get("should_scale", False)

    decision = "hold"
    new_topic = topic

    if should_scale:
        decision = "scale"
    else:
        decision = "mutate"
        new_topic = mutate_topic(topic)

        safe_save(os.path.join(DATA_DIR, "current_topic.json"), {
            "topic": new_topic
        })

    return {
        "status": "evolution_complete",
        "previous_topic": topic,
        "new_topic": new_topic,
        "decision": decision,
        "based_on": {
            "validation_score": last.get("validation_score"),
            "should_scale": should_scale
        }
    }

