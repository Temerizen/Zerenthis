from pathlib import Path
import json
import py_compile

IDENTITY = Path("backend/data/identity_state.json")
ENGINE = Path("backend/app/cognition/identity_engine.py")

# -------------------------
# 1) FORCE RESET CURRENT STATE
# -------------------------
state = json.loads(IDENTITY.read_text(encoding="utf-8"))

traits = state.setdefault("traits", {})
traits["confidence"] = 0.68
traits["aggression"] = 0.48
traits["curiosity"] = 0.46

# soften runaway prefs a bit without deleting learning
prefs = state.setdefault("preferences", {})
for key in list(prefs.keys()):
    try:
        prefs[key] = round(float(prefs[key]) * 0.55, 4)
    except Exception:
        pass

state["last_reflection"] = "trait reset applied"
IDENTITY.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

# -------------------------
# 2) PATCH ENGINE WITH HARDER ANTI-LOCK LOGIC
# -------------------------
code = ENGINE.read_text(encoding="utf-8")

old = """    if repeated_count >= 3:
        curiosity += 0.015
        aggression -= 0.01

    if repeated_count >= 5:
        confidence -= 0.01
        curiosity += 0.02"""

new = """    if repeated_count >= 3:
        curiosity += 0.04
        aggression -= 0.03

    if repeated_count >= 5:
        confidence -= 0.05
        aggression -= 0.04
        curiosity += 0.06

    if repeated_count >= 8:
        confidence -= 0.08
        aggression -= 0.06
        curiosity += 0.1"""

if old in code:
    code = code.replace(old, new)

old2 = """    # HARD RESET IF EXTREME LOCK DETECTED
    if confidence > 0.95 and aggression > 0.95 and curiosity < 0.05:
        confidence = 0.7
        aggression = 0.5
        curiosity = 0.4
"""

new2 = """    # HARD RESET IF EXTREME LOCK DETECTED
    if confidence > 0.9 and aggression > 0.9 and curiosity < 0.1:
        confidence = 0.65
        aggression = 0.45
        curiosity = 0.5

    # HARD RESET IF REPETITION LOCK DETECTED
    if repeated_count >= 10:
        confidence = min(confidence, 0.62)
        aggression = min(aggression, 0.42)
        curiosity = max(curiosity, 0.58)
"""

if old2 in code:
    code = code.replace(old2, new2)

ENGINE.write_text(code, encoding="utf-8")
py_compile.compile(str(ENGINE), doraise=True)

print("RUNTIME_TRAIT_LOCK_FIX_APPLIED")
