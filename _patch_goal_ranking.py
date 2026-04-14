from pathlib import Path
import re

path = Path(r"backend\app\execution\runner.py")
text = path.read_text(encoding="utf-8")

replacement = '''    goal_ranking_simple = []

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
'''

pattern = r'^\s*goal_ranking_simple\s*=\s*\[.*?^\s*observation\s*=\s*build_observation\(goal,\s*goal_ranking_simple,\s*chosen,\s*ranked,\s*latest_result\)\s*$'
new_text, count = re.subn(pattern, replacement, text, flags=re.S | re.M)

if count != 1:
    raise SystemExit(f"Patch failed. goal_ranking_simple replacements: {count}")

path.write_text(new_text, encoding="utf-8")
print("Patched goal_ranking_simple successfully.")
