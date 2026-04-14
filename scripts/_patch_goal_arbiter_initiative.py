from pathlib import Path
import py_compile

p = Path("backend/app/cognition/goal_arbiter.py")
code = p.read_text(encoding="utf-8")

if 'INITIATIVE_PATH = BASE / "initiative_goals.json"' not in code:
    code = code.replace(
        'MISSION_PATH = BASE / "active_mission.json"',
        'MISSION_PATH = BASE / "active_mission.json"\nINITIATIVE_PATH = BASE / "initiative_goals.json"'
    )

old = """    goals = payload.get("goals", []) if isinstance(payload, dict) else []
    mission_payload = _load_json(MISSION_PATH, {})
    mission = mission_payload.get("mission") if isinstance(mission_payload, dict) else {}
    blocked_tasks = mission.get("blocked_tasks", []) if isinstance(mission, dict) else []"""

new = """    goals = payload.get("goals", []) if isinstance(payload, dict) else []
    initiative_payload = _load_json(INITIATIVE_PATH, {})
    initiative_goals = initiative_payload.get("initiative_goals", []) if isinstance(initiative_payload, dict) else []
    if isinstance(initiative_goals, list) and initiative_goals:
        goals = list(goals) + list(initiative_goals)
    mission_payload = _load_json(MISSION_PATH, {})
    mission = mission_payload.get("mission") if isinstance(mission_payload, dict) else {}
    blocked_tasks = mission.get("blocked_tasks", []) if isinstance(mission, dict) else []"""

if old in code:
    code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("GOAL_ARBITER_INITIATIVE_PATCHED")
