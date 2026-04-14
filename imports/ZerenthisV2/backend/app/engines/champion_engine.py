import os, json, random, time

DATA_DIR = "backend/data"

def load(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def diversify(topic):
    variations = [
        topic.replace("money", "income"),
        topic.replace("fast", "daily"),
        topic + "_for_students",
        topic + "_for_beginners",
        topic + "_no_skills",
        "ai_" + topic,
        topic.replace("side_income", "online_income"),
        topic.replace("blueprint", "guide")
    ]
    return random.choice(variations)

def run():
    perf = load(os.path.join(DATA_DIR, "performance_log.json"), [])
    champ = load(os.path.join(DATA_DIR, "champion.json"), {})
    current = load(os.path.join(DATA_DIR, "current_topic.json"), {"topic": "unknown"})

    topic = current.get("topic")
    last = perf[-1] if perf else {}

    score = last.get("validation_score", 0)
    should_scale = last.get("should_scale", False)

    challengers = load(os.path.join(DATA_DIR, "challengers.json"), [])

    # Add current to challengers pool
    challengers.append({
        "topic": topic,
        "score": score,
        "ts": int(time.time())
    })

    # Keep top 5
    challengers = sorted(challengers, key=lambda x: x["score"], reverse=True)[:5]
    save(os.path.join(DATA_DIR, "challengers.json"), challengers)

    # Determine champion
    best = challengers[0] if challengers else {"topic": topic, "score": score}

    previous_champ = champ.get("topic")
    new_champ = best["topic"]

    save(os.path.join(DATA_DIR, "champion.json"), best)

    # Decide next topic
    if should_scale:
        next_topic = new_champ
        decision = "scale_champion"
    else:
        next_topic = diversify(new_champ)
        decision = "explore_new"

    save(os.path.join(DATA_DIR, "current_topic.json"), {
        "topic": next_topic
    })

    return {
        "status": "champion_cycle_complete",
        "previous_champion": previous_champ,
        "new_champion": new_champ,
        "decision": decision,
        "next_topic": next_topic,
        "top_challengers": challengers
    }
