from pathlib import Path
import json
import time
import random

IDENTITY = Path("backend/data/identity_state.json")
THOUGHTS = Path("backend/data/thought_stream.json")

def read_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# -------------------------
# DECISION ENGINE CORE
# -------------------------

TASKS = [
    "revenue_scan",
    "builder_handoff",
    "toolbox_strategy",
    "create_thought_engine"
]

def compute_scores(identity, thoughts):
    prefs = identity.get("preferences", {})
    history = identity.get("history", {}).get("repeated_tasks", {})
    
    # Count recent usage (fatigue)
    recent = {}
    for t in thoughts[-20:]:
        task = t.get("chosen_task")
        if task:
            recent[task] = recent.get(task, 0) + 1

    scores = {}

    for task in TASKS:
        base = 1.0

        # Preference boost
        pref = prefs.get(task, 1.0)

        # History reinforcement
        hist = history.get(task, 0)
        history_boost = min(hist * 0.05, 2.0)

        # Fatigue penalty
        fatigue = recent.get(task, 0)
        fatigue_penalty = fatigue * 0.3

        # Exploration bonus
        exploration = 1.0 if fatigue == 0 else 0.0

        score = (
            base +
            pref +
            history_boost +
            exploration -
            fatigue_penalty
        )

        scores[task] = round(score, 4)

    return scores

def pick_task(scores):
    # Softmax-like selection
    total = sum(max(v, 0.01) for v in scores.values())
    r = random.uniform(0, total)
    upto = 0
    for task, score in scores.items():
        val = max(score, 0.01)
        if upto + val >= r:
            return task
        upto += val
    return random.choice(list(scores.keys()))

# -------------------------
# EXECUTION STEP
# -------------------------

identity = read_json(IDENTITY, {})
thoughts = read_json(THOUGHTS, [])

scores = compute_scores(identity, thoughts)
chosen = pick_task(scores)

# Log thought
entry = {
    "timestamp": time.time(),
    "current_goal": identity.get("last_goal", "autonomy_cycle"),
    "chosen_task": chosen,
    "result": "pending",
    "reasoning": f"Decision engine selected based on scoring: {scores}",
    "reflection": "",
    "extra": {
        "scores": scores
    }
}

thoughts.append(entry)

# Update identity last_task
identity["last_task"] = chosen
identity["last_updated"] = time.time()

write_json(THOUGHTS, thoughts)
write_json(IDENTITY, identity)

print("DECISION_ENGINE_ACTIVE")
print("CHOSEN_TASK:", chosen)
print("SCORES:", scores)

