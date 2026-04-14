from pathlib import Path
import json
import time
import random
from backend.app.core.goal_schema import enforce_goal_schema
from backend.app.core.meta_intelligence import update_meta

QUEUE_PATH = Path("backend/data/task_queue.json")
LOG_PATH = Path("backend/data/task_log.json")
PERF_PATH = Path("backend/data/performance_memory.json")
IDENTITY_PATH = Path("backend/data/identity_state.json")
GOAL_PATH = Path("backend/data/active_goal.json")
GOALS_PATH = Path("backend/data/active_goals.json")
OBS_PATH = Path("backend/data/self_observation.json")

def load_json(path, default):
    if path.exists():
        try:
            return json.load(open(path, "r", encoding="utf-8"))
        except Exception:
            return default
    return default

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2)

def now():
    return time.time()

def make_id():
    return time.time_ns()

def load_queue():
    return load_json(QUEUE_PATH, [])

def save_queue(q):
    save_json(QUEUE_PATH, q)

def load_log():
    return load_json(LOG_PATH, [])

def save_log(log):
    save_json(LOG_PATH, log[-100:])

def load_perf():
    perf = load_json(PERF_PATH, {})
    for _, v in perf.items():
        if "total" not in v and "total_score" in v:
            v["total"] = v["total_score"]
        if "runs" not in v:
            v["runs"] = 0
        if "avg_score" not in v:
            total = v.get("total", 0.0)
            runs = v.get("runs", 0)
            v["avg_score"] = (total / runs) if runs else 0.0
    return perf

def save_perf(p):
    save_json(PERF_PATH, p)

def load_identity():
    return load_json(IDENTITY_PATH, None)

def save_identity(i):
    save_json(IDENTITY_PATH, i)

def load_goal():
    return load_json(GOAL_PATH, None)

def save_goal(g):
    save_json(GOAL_PATH, g)

def load_goals():
    goals = load_json(GOALS_PATH, None)
    if goals:
        return goals
    return [
        {
            "objective": "improve proof and reality feedback",
            "priority": "high",
            "weight": 1.0,
            "source": "bundle_f_default"
        },
        {
            "objective": "expand revenue discovery and opportunity mapping",
            "priority": "medium",
            "weight": 0.9,
            "source": "bundle_f_default"
        },
        {
            "objective": "strengthen system strategy and leverage",
            "priority": "medium",
            "weight": 0.95,
            "source": "bundle_f_default"
        }
    ]

def save_goals(goals):
    save_json(GOALS_PATH, goals)

def load_observation():
    return load_json(OBS_PATH, {})

def save_observation(o):
    save_json(OBS_PATH, o)

def evaluate_result(result):
    s = result.get("status")
    if s == "failed":
        return -1.0
    if s == "retrying":
        return 0.0
    return 1.0

def create_plan():
    return ["revenue_scan", "toolbox_strategy", "builder_handoff"]

def default_identity():
    return {
        "mode": "builder",
        "confidence": 0.5,
        "dominant_preference": "toolbox_strategy",
        "drive": "improve_proof",
        "updated_at": now()
    }

def infer_drive_from_goal(goal):
    objective = ""
    if isinstance(goal, dict):
        objective = goal.get("objective", "").lower()

    if "revenue" in objective or "money" in objective or "profit" in objective:
        return "expand_revenue"
    if "proof" in objective or "reality" in objective or "evidence" in objective:
        return "improve_proof"
    if "strategy" in objective or "leverage" in objective:
        return "strengthen_strategy"
    return "general_growth"

def task_goal_bias(task, goal):
    objective = ""
    if isinstance(goal, dict):
        objective = goal.get("objective", "").lower()

    if task == "revenue_scan" and any(k in objective for k in ["revenue", "money", "profit", "opportunity"]):
        return 0.8
    if task == "toolbox_strategy" and any(k in objective for k in ["strategy", "leverage", "proof", "reality"]):
        return 0.8
    if task == "builder_handoff" and any(k in objective for k in ["build", "improve", "system", "proof", "reality"]):
        return 0.6
    return 0.0

def recent_penalty(task, log):
    recent = log[-8:]
    repeats = 0
    for entry in recent:
        result = entry.get("result", {})
        if result.get("task") == task:
            repeats += 1
    return repeats * 0.35

def exploration_bonus(task, log):
    recent = log[-12:]
    seen = any(entry.get("result", {}).get("task") == task for entry in recent)
    return 0.0 if seen else 0.45

def goal_recency_penalty(goal, observation):
    chosen_goal = ""
    if isinstance(observation, dict):
        g = observation.get("goal", {})
        if isinstance(g, dict):
            chosen_goal = g.get("objective", "")
    if chosen_goal and isinstance(goal, dict) and goal.get("objective", "") == chosen_goal:
        return 0.15
    return 0.0

def goal_priority_bonus(goal):
    priority = str(goal.get("priority", "medium")).lower()
    if priority == "high":
        return 0.35
    if priority == "low":
        return -0.1
    return 0.15

def score_goal(goal, perf, identity, observation):
    # NORMALIZE GOAL (critical)
    if isinstance(goal, str):
        goal = {"objective": goal}
    elif not isinstance(goal, dict):
        return 0.0

    objective = str(goal.get("objective", "")).lower()
    weight = float(goal.get("weight", 1.0) or 1.0)
    drive = identity.get("drive", "") if isinstance(identity, dict) else ""

    score = weight + goal_priority_bonus(goal)

    if "revenue" in objective and drive == "expand_revenue":
        score += 0.4
    if "proof" in objective and drive == "improve_proof":
        score += 0.4
    if "strategy" in objective and drive == "strengthen_strategy":
        score += 0.4

    if "toolbox_strategy" in perf and "strategy" in objective:
        score += perf["toolbox_strategy"].get("avg_score", 0.0) * 0.15
    if "revenue_scan" in perf and "revenue" in objective:
        score += perf["revenue_scan"].get("avg_score", 0.0) * 0.15
    if "builder_handoff" in perf and ("proof" in objective or "build" in objective):
        score += perf["builder_handoff"].get("avg_score", 0.0) * 0.15

    score -= goal_recency_penalty(goal, observation)
    score += random.uniform(-0.08, 0.12)

    return round(score, 4)


def select_active_goal(goals, perf, identity, observation):
    ranked = []
    for goal in goals:
        goal = enforce_goal_schema(goal)
        if goal is None:
            continue
        goal = enforce_goal_schema(goal)
        if goal is None:
            continue
        ranked.append({
            "goal": goal,
            "score": score_goal(goal, perf, identity, observation)
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[0]["goal"], ranked

def score_task(task, perf, identity, goal, log):
    base = perf.get(task, {}).get("avg_score", 0.0)

    preference_bonus = 0.3 if task == identity.get("dominant_preference") else 0.0
    goal_bonus = task_goal_bias(task, goal)
    novelty_bonus = exploration_bonus(task, log)
    fatigue_penalty = recent_penalty(task, log)
    exploration_noise = random.uniform(-0.15, 0.25)

    total = base + preference_bonus + goal_bonus + novelty_bonus + exploration_noise - fatigue_penalty

    return round(total, 4), {
        "base": round(base, 4),
        "preference_bonus": round(preference_bonus, 4),
        "goal_bonus": round(goal_bonus, 4),
        "novelty_bonus": round(novelty_bonus, 4),
        "fatigue_penalty": round(fatigue_penalty, 4),
        "exploration_noise": round(exploration_noise, 4)
    }

def select_next_task(plan, perf, identity, goal, log):
    ranked = []
    for task in plan:
        score, parts = score_task(task, perf, identity, goal, log)
        ranked.append({
            "task": task,
            "score": score,
            "parts": parts
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[0]["task"], ranked

def update_identity(identity, task, result, perf, goal):
    if not identity:
        identity = default_identity()

    if result.get("status") == "failed":
        identity["mode"] = "recovery"
    else:
        identity["mode"] = "strategist"
        identity["dominant_preference"] = task

    identity["drive"] = infer_drive_from_goal(goal)

    scores = [v.get("avg_score", 0.0) for v in perf.values()]
    if scores:
        identity["confidence"] = round(sum(scores) / len(scores), 4)

    identity["updated_at"] = now()
    return identity

def build_observation(goal, goal_ranking, chosen, ranked, result):
    return {
        "timestamp": now(),
        "goal": goal,
        "goal_ranking": goal_ranking,
        "chosen_task": chosen,
        "result_status": result.get("status"),
        "decision_ranking": ranked,
        "insight": f"selected {chosen} under directed goal pressure"
    }

ACTIVE = {"pending", "running", "retrying"}

def add_task(task, queue):
    queue.append({
        "id": make_id(),
        "task": task,
        "status": "pending",
        "attempts": 0,
        "max_attempts": 2,
        "created_at": now()
    })

def run_task(task):
    q = load_queue()
    add_task(task, q)
    save_queue(q)
    return {"status": "queued", "task": task}

def get_goals():
    goals = load_goals()
    observation = load_observation()
    return {
        "status": "ok",
        "goals": goals,
        "last_observation": observation
    }

def reset_goals():
    goals = [
        {
            "objective": "improve proof and reality feedback",
            "priority": "high",
            "weight": 1.0,
            "source": "bundle_f_reset"
        },
        {
            "objective": "expand revenue discovery and opportunity mapping",
            "priority": "medium",
            "weight": 0.9,
            "source": "bundle_f_reset"
        },
        {
            "objective": "strengthen system strategy and leverage",
            "priority": "medium",
            "weight": 0.95,
            "source": "bundle_f_reset"
        }
    ]
    save_goals(goals)
    return {"status": "reset", "goals": goals}

def execute_all(limit=10):
    queue = load_queue()
    log = load_log()
    perf = load_perf()
    identity = load_identity() or default_identity()
    goals = load_goals()
    previous_observation = load_observation()

    goal, goal_ranked = select_active_goal(goals, perf, identity, previous_observation)

    try:
        if isinstance(goal, str):
            goal = {"id": goal, "objective": goal, "goal_type": "expansion", "priority": 0.5}
        elif isinstance(goal, dict) and "id" not in goal and "objective" in goal:
            goal["id"] = goal["objective"]

        if isinstance(goal, dict):
            update_meta(goal)
    except Exception as e:
        print(f"[META ERROR] {e}")

    try:
        goal = enforce_goal_schema(goal)
        if goal is not None:
            update_meta(goal)
    except Exception as e:
        print(f"[META ERROR] {e}")
    # save_goal(goal)  # DISABLED: prevents overwrite of cognitive goal system

    plan = create_plan()
    chosen, ranked = select_next_task(plan, perf, identity, goal, log)

    if not any(q.get("task") == chosen and q.get("status") in ACTIVE for q in queue):
        add_task(chosen, queue)

    results = []
    processed = 0
    latest_result = None

    for item in queue:
        if processed >= limit:
            break

        if item.get("status") in ["pending", "retrying"]:
            item["status"] = "running"
            item["attempts"] += 1

            time.sleep(0.05)

            if random.random() < 0.1:
                if item["attempts"] < item["max_attempts"]:
                    item["status"] = "retrying"
                else:
                    item["status"] = "failed"
            else:
                item["status"] = "done"

            item["completed_at"] = now()

            result = {
                "status": item["status"],
                "task": item["task"]
            }
            latest_result = result
            item["result"] = result

            log.append({
                "task": item.copy(),
                "result": result,
                "timestamp": now()
            })

            t = item["task"]
            if t not in perf:
                perf[t] = {"runs": 0, "total": 0.0, "avg_score": 0.0}

            p = perf[t]
            if "total" not in p:
                p["total"] = p.get("total_score", 0.0)

            score = evaluate_result(result)
            p["runs"] += 1
            p["total"] += score
            p["avg_score"] = p["total"] / p["runs"]

            identity = update_identity(identity, t, result, perf, goal)

            results.append(result)
            processed += 1

    if latest_result is None:
        latest_result = {"status": "idle", "task": chosen}
    goal_ranking_simple = []

    for item in goal_ranked:
        if not isinstance(item, dict):
            continue

        g = item.get("goal")

        if isinstance(g, str):
            g = {"objective": g}
        elif not isinstance(g, dict):
            g = {}

        goal_ranking_simple.append({
            "objective": g.get("objective") or g.get("id") or g.get("reason"),
            "priority": g.get("priority"),
            "score": item.get("score")
        })

    observation = build_observation(goal, goal_ranking_simple, chosen, ranked, latest_result)

    save_queue(queue)
    save_log(log)
    save_perf(perf)
    save_identity(identity)
    # save_goal(goal)  # DISABLED: prevents overwrite of cognitive goal system
    save_goals(goals)
    save_observation(observation)

    return results




