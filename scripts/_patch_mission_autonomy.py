from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")

if "from backend.app.cognition.mission_engine import build_or_update_mission, advance_mission_progress" not in code:
    code = code.replace(
        "from backend.app.cognition.feedback_engine import apply_feedback",
        "from backend.app.cognition.feedback_engine import apply_feedback\nfrom backend.app.cognition.mission_engine import build_or_update_mission, advance_mission_progress"
    )

old = """                    build_active_plan()
                    execute_active_goal()
                    advance_active_plan()
                    record_execution()
                    apply_feedback()"""

new = """                    build_active_plan()
                    build_or_update_mission()
                    execute_active_goal()
                    advance_active_plan()
                    record_execution()
                    apply_feedback()
                    advance_mission_progress()"""

if old in code and "build_or_update_mission()" not in code:
    code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("AUTONOMY_MISSION_PATCHED")
