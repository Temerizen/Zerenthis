from pathlib import Path
import py_compile

p = Path("backend/app/cognition/self_influence.py")
code = p.read_text(encoding="utf-8")

if "def apply_self_influence(" not in code:
    code = code.rstrip() + """

def apply_self_influence(task_name: str, base_score: float) -> float:
    \"""
    Backward-compatible wrapper for decision_engine integration.
    Keeps the existing cognition_influence logic and simply adds it
    to the provided base score.
    \"""
    try:
        bonus = cognition_influence({"task": task_name, "score": base_score})
        return round(float(base_score) + float(bonus), 4)
    except Exception:
        return float(base_score)
"""
    p.write_text(code, encoding="utf-8")

py_compile.compile(str(p), doraise=True)
print("SELF_INFLUENCE WRAPPER ADDED")
