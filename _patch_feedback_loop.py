from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")

if "record_execution" not in code:
    code = code.replace(
        "advance_active_plan()",
        "advance_active_plan()\n                    record_execution()\n                    apply_feedback()"
    )

if "from backend.app.cognition.execution_memory import record_execution" not in code:
    code = code.replace(
        "from backend.app.cognition.plan_engine import build_active_plan, advance_active_plan",
        "from backend.app.cognition.plan_engine import build_active_plan, advance_active_plan\nfrom backend.app.cognition.execution_memory import record_execution\nfrom backend.app.cognition.feedback_engine import apply_feedback"
    )

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)

print("ADAPTIVE_LOOP_PATCHED")
