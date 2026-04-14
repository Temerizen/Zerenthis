from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")
original = code

if "from backend.app.cognition.plan_engine import build_active_plan, advance_active_plan" not in code:
    code = code.replace(
        "from backend.app.cognition.goal_executor import execute_active_goal",
        "from backend.app.cognition.goal_executor import execute_active_goal\nfrom backend.app.cognition.plan_engine import build_active_plan, advance_active_plan"
    )

old = """                if STATE["cycle_count"] % 4 == 0:
                    run_goal_generation()
                    select_active_goal()
                    execute_active_goal()"""

new = """                if STATE["cycle_count"] % 4 == 0:
                    run_goal_generation()
                    select_active_goal()
                    build_active_plan()
                    execute_active_goal()
                    advance_active_plan()"""

if old in code and "build_active_plan()" not in code:
    code = code.replace(old, new)

if code == original:
    print("NO_PLAN_AUTONOMY_CHANGES")
else:
    p.write_text(code, encoding="utf-8")
    py_compile.compile(str(p), doraise=True)
    print("AUTONOMY_PLANNING_PATCHED")
