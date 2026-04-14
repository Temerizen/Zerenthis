from pathlib import Path
import py_compile

p = Path("backend/app/cognition/execution_memory.py")
code = p.read_text(encoding="utf-8")

if "evaluate_outcome" not in code:
    code = code.replace(
        "event = {",
        "from backend.app.cognition.outcome_engine import evaluate_outcome\n    outcome_data = evaluate_outcome(last_done.get(\"task\"))\n\n    event = {"
    )

    code = code.replace(
        '"outcome": "success"',
        '"outcome": outcome_data.get("outcome"), "score": outcome_data.get("score"), "reason": outcome_data.get("reason")'
    )

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)

print("EXECUTION_MEMORY_PATCHED")
