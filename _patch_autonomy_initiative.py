from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")

if "from backend.app.cognition.initiative_engine import build_initiative_goals" not in code:
    code = code.replace(
        "from backend.app.cognition.conflict_engine import resolve_conflicts",
        "from backend.app.cognition.conflict_engine import resolve_conflicts\nfrom backend.app.cognition.initiative_engine import build_initiative_goals"
    )

old = """                    run_goal_generation()
                    select_active_goal()
                    build_active_plan()
                    build_or_update_mission()
                    resolve_conflicts()"""

new = """                    run_goal_generation()
                    build_initiative_goals()
                    select_active_goal()
                    build_active_plan()
                    build_or_update_mission()
                    resolve_conflicts()"""

if old in code and "build_initiative_goals()" not in code:
    code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("AUTONOMY_INITIATIVE_PATCHED")
