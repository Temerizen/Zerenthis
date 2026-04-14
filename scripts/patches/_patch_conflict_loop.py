from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")

if "from backend.app.cognition.conflict_engine import resolve_conflicts" not in code:
    code = code.replace(
        "from backend.app.cognition.mission_engine import build_or_update_mission, advance_mission_progress",
        "from backend.app.cognition.mission_engine import build_or_update_mission, advance_mission_progress\nfrom backend.app.cognition.conflict_engine import resolve_conflicts"
    )

old = """                    build_or_update_mission()
                    execute_active_goal()
                    advance_active_plan()
                    record_execution()
                    apply_feedback()
                    advance_mission_progress()"""

new = """                    build_or_update_mission()
                    resolve_conflicts()
                    execute_active_goal()
                    advance_active_plan()
                    record_execution()
                    apply_feedback()
                    advance_mission_progress()"""

if old in code and "resolve_conflicts()" not in code:
    code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)

print("CONFLICT_LOOP_PATCHED")
