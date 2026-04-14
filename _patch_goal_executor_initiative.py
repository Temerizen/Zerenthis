from pathlib import Path
import py_compile

p = Path("backend/app/cognition/goal_executor.py")
code = p.read_text(encoding="utf-8")

insert_after = """    if goal_type == "companion":
        return {
            "task": "toolbox_strategy",
            "mode": "companion_improvement",
            "reason": goal.get("reason", ""),
        }
"""

addition = """
    if goal_type == "initiative":
        if goal_id == "initiate_exploration_shift":
            return {
                "task": "revenue_scan",
                "mode": "initiative_explore",
                "reason": goal.get("reason", ""),
            }

        if goal_id == "initiate_recovery_mode":
            return {
                "task": "create_thought_engine",
                "mode": "initiative_recover",
                "reason": goal.get("reason", ""),
            }

        if goal_id == "initiate_mission_support":
            return {
                "task": "builder_handoff",
                "mode": "initiative_support",
                "reason": goal.get("reason", ""),
            }

        if goal_id == "initiate_companion_growth":
            return {
                "task": "toolbox_strategy",
                "mode": "initiative_companion_growth",
                "reason": goal.get("reason", ""),
            }
"""

if addition not in code and insert_after in code:
    code = code.replace(insert_after, insert_after + addition)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("GOAL_EXECUTOR_INITIATIVE_PATCHED")
