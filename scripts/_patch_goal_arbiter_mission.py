from pathlib import Path
import py_compile

p = Path("backend/app/cognition/goal_arbiter.py")
code = p.read_text(encoding="utf-8")

if 'MISSION_PATH = BASE / "active_mission.json"' not in code:
    code = code.replace(
        'ACTIVE_GOAL_PATH = BASE / "active_goal.json"',
        'ACTIVE_GOAL_PATH = BASE / "active_goal.json"\nMISSION_PATH = BASE / "active_mission.json"'
    )

old = """def select_active_goal() -> Dict[str, Any]:
    payload = _load_json(GOALS_PATH, {})
    goals = payload.get("goals", []) if isinstance(payload, dict) else []"""

new = """def select_active_goal() -> Dict[str, Any]:
    payload = _load_json(GOALS_PATH, {})
    goals = payload.get("goals", []) if isinstance(payload, dict) else []
    mission_payload = _load_json(MISSION_PATH, {})
    mission = mission_payload.get("mission") if isinstance(mission_payload, dict) else {}
    blocked_tasks = mission.get("blocked_tasks", []) if isinstance(mission, dict) else []"""

if old in code:
    code = code.replace(old, new)

old2 = """        enriched = dict(goal)
        enriched["_score"] = _score_goal(goal)
        scored.append(enriched)"""

new2 = """        enriched = dict(goal)
        enriched["_score"] = _score_goal(goal)

        goal_id = str(enriched.get("id", ""))
        blocked_hit = False
        for blocked in blocked_tasks:
            if blocked and blocked in goal_id:
                blocked_hit = True
                break

        if blocked_hit:
            enriched["_score"] = round(float(enriched["_score"]) - 0.5, 4)
            enriched["_blocked_penalty"] = True

        scored.append(enriched)"""

if old2 in code:
    code = code.replace(old2, new2)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("GOAL_ARBITER_MISSION_PATCHED")
