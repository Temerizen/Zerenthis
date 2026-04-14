from pathlib import Path
import py_compile

p = Path("backend/app/cognition/identity_engine.py")
code = p.read_text(encoding="utf-8")

inject = """
    # HARD RESET IF EXTREME LOCK DETECTED
    if confidence > 0.95 and aggression > 0.95 and curiosity < 0.05:
        confidence = 0.7
        aggression = 0.5
        curiosity = 0.4
"""

marker = 'traits["confidence"] = _clamp(confidence)'

if inject not in code:
    code = code.replace(marker, inject + "\n    " + marker)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("HARD_RESET_INJECTED")
