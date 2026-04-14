from pathlib import Path

path = Path(r"backend\app\execution\runner.py")
text = path.read_text(encoding="utf-8")

needle = '    goal, goal_ranked = select_active_goal(goals, perf, identity, previous_observation)\n'
insert = '''    goal, goal_ranked = select_active_goal(goals, perf, identity, previous_observation)

    try:
        if isinstance(goal, str):
            goal = {"id": goal, "objective": goal, "goal_type": "expansion", "priority": 0.5}
        elif isinstance(goal, dict) and "id" not in goal and "objective" in goal:
            goal["id"] = goal["objective"]

        if isinstance(goal, dict):
            update_meta(goal)
    except Exception as e:
        print(f"[META ERROR] {e}")
'''

if needle not in text:
    raise SystemExit("Could not find execute_all goal selection line.")

text = text.replace(needle, insert, 1)
path.write_text(text, encoding="utf-8")
print("Patched execute_all meta hook.")
