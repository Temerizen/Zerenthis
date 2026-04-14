from pathlib import Path
import py_compile

p = Path("backend/app/cognition/feedback_engine.py")
code = p.read_text(encoding="utf-8")

code = code.replace(
    'if event.get("outcome") == "success":\n            prefs[task] += 0.05\n        else:\n            prefs[task] -= 0.05',
    'score = float(event.get("score", 0.0) or 0.0)\n        prefs[task] += score'
)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)

print("FEEDBACK_WEIGHTED_PATCHED")
