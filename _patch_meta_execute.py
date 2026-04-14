from pathlib import Path

path = Path(r"backend\app\execution\runner.py")
text = path.read_text(encoding="utf-8")

# 1. Ensure imports exist
if "from backend.app.core.goal_schema import enforce_goal_schema" not in text:
    text = text.replace(
        "import random",
        "import random\nfrom backend.app.core.goal_schema import enforce_goal_schema\nfrom backend.app.core.meta_intelligence import update_meta"
    )

# 2. Inject meta update immediately after active goal selection
needle = '    goal, goal_ranked = select_active_goal(goals, perf, identity, previous_observation)\n'
insert = '''    goal, goal_ranked = select_active_goal(goals, perf, identity, previous_observation)

    try:
        goal = enforce_goal_schema(goal)
        if goal is not None:
            update_meta(goal)
    except Exception as e:
        print(f"[META ERROR] {e}")
'''

if needle not in text:
    raise SystemExit("Patch failed. Could not find active goal selection line.")

text = text.replace(needle, insert, 1)

path.write_text(text, encoding="utf-8")
print("Patched execute_all meta hook successfully.")
