from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")
original = code

if "from backend.app.cognition.goal_generator import run_goal_generation" not in code:
    code = code.replace(
        "from backend.app.cognition.reflection_engine import run_reflection",
        "from backend.app.cognition.reflection_engine import run_reflection\nfrom backend.app.cognition.goal_generator import run_goal_generation\nfrom backend.app.cognition.goal_arbiter import select_active_goal\nfrom backend.app.cognition.goal_executor import execute_active_goal"
    )

old = """                if STATE["cycle_count"] % 3 == 0:
                    run_reflection(10)"""

new = """                if STATE["cycle_count"] % 3 == 0:
                    run_reflection(10)

                if STATE["cycle_count"] % 4 == 0:
                    run_goal_generation()
                    select_active_goal()
                    execute_active_goal()"""

if old in code and "run_goal_generation()" not in code:
    code = code.replace(old, new)

if code == original:
    print("NO_AUTONOMY_CHANGES")
else:
    p.write_text(code, encoding="utf-8")
    py_compile.compile(str(p), doraise=True)
    print("AUTONOMY_GOAL_BINDING_PATCHED")
