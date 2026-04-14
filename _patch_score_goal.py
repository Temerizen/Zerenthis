from pathlib import Path
import re

path = Path(r"backend\app\execution\runner.py")
text = path.read_text(encoding="utf-8")

replacement = '''def score_goal(goal, perf, identity, observation):
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
'''

pattern = r"def score_goal\(goal, perf, identity, observation\):.*?^\s*def select_active_goal\("
new_text, count = re.subn(
    pattern,
    replacement + "\n\ndef select_active_goal(",
    text,
    flags=re.S | re.M,
)

if count != 1:
    raise SystemExit(f"Patch failed. score_goal block replacements: {count}")

path.write_text(new_text, encoding="utf-8")
print("Patched score_goal successfully.")
