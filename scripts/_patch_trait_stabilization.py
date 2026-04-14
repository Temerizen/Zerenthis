from pathlib import Path
import py_compile

p = Path("backend/app/cognition/identity_engine.py")
code = p.read_text(encoding="utf-8")

old = """def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, round(float(value), 4)))"""

new = """def _clamp(value: float, low: float = 0.15, high: float = 0.85) -> float:
    return max(low, min(high, round(float(value), 4)))"""

if old in code:
    code = code.replace(old, new)

old2 = """def _update_traits(state: Dict[str, Any], outcome: str, repeated_count: int, goal_aligned: bool) -> None:
    traits = state.setdefault("traits", {})
    confidence = float(traits.get("confidence", 0.5))
    aggression = float(traits.get("aggression", 0.35))
    curiosity = float(traits.get("curiosity", 0.6))

    if outcome == "success":
        confidence += 0.04
        aggression += 0.01
    elif outcome == "failure":
        confidence -= 0.05
        aggression -= 0.02
        curiosity += 0.03
    else:
        curiosity += 0.01

    if repeated_count >= 3:
        curiosity -= 0.02

    if goal_aligned:
        confidence += 0.01
    else:
        curiosity += 0.02

    traits["confidence"] = _clamp(confidence)
    traits["aggression"] = _clamp(aggression)
    traits["curiosity"] = _clamp(curiosity)"""

new2 = """def _update_traits(state: Dict[str, Any], outcome: str, repeated_count: int, goal_aligned: bool) -> None:
    traits = state.setdefault("traits", {})
    confidence = float(traits.get("confidence", 0.5))
    aggression = float(traits.get("aggression", 0.35))
    curiosity = float(traits.get("curiosity", 0.6))

    # soft baseline recovery toward balance
    confidence += (0.6 - confidence) * 0.03
    aggression += (0.45 - aggression) * 0.03
    curiosity += (0.55 - curiosity) * 0.04

    if outcome == "success":
        confidence += 0.015
        aggression += 0.005
    elif outcome == "failure":
        confidence -= 0.03
        aggression -= 0.015
        curiosity += 0.04
    else:
        curiosity += 0.01

    if repeated_count >= 3:
        curiosity += 0.015
        aggression -= 0.01

    if repeated_count >= 5:
        confidence -= 0.01
        curiosity += 0.02

    if goal_aligned:
        confidence += 0.005
    else:
        curiosity += 0.02

    traits["confidence"] = _clamp(confidence)
    traits["aggression"] = _clamp(aggression)
    traits["curiosity"] = _clamp(curiosity)"""

if old2 in code:
    code = code.replace(old2, new2)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("TRAIT_STABILIZATION_PATCHED")
