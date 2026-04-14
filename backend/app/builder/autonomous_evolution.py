import os, time
from typing import Dict

from backend.app.builder.builder_intelligence import analyze_change
from backend.app.builder.safe_builder import apply_safe_change
from backend.app.builder.evolution_brain import propose_variants
from backend.app.builder.evolution_memory import record

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
TARGET_FILE = os.path.join(BASE_DIR, "backend/app/test_file.py")

def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _score_simple(old: str, new: str) -> float:
    # Simple heuristic: prefer shorter, clearer code (tiny bias)
    # You can replace this later with real metrics (conversion, pnl, etc.)
    return max(0.0, 1.0 - (len(new) / max(len(old), 1))) + 0.5

def run_once() -> Dict:
    if not os.path.exists(TARGET_FILE):
        return {"status": "error", "reason": "target_missing", "path": TARGET_FILE}

    old_code = _read(TARGET_FILE)

    # --- propose 2 variants ---
    v1, v2 = propose_variants(2)

    # --- analyze both ---
    a1 = analyze_change(TARGET_FILE, old_code, v1)
    a2 = analyze_change(TARGET_FILE, old_code, v2)

    # --- filter approved candidates ---
    candidates = []
    if a1.get("status") == "approved":
        candidates.append(("v1", v1, a1))
    if a2.get("status") == "approved":
        candidates.append(("v2", v2, a2))

    if not candidates:
        run = {"status": "skipped", "reason": "no_approved_variants", "a1": a1, "a2": a2}
        record(run)
        return run

    # --- score candidates ---
    scored = []
    for tag, code, analysis in candidates:
        s = _score_simple(old_code, code)
        scored.append((s, tag, code, analysis))

    # pick best
    scored.sort(reverse=True, key=lambda x: x[0])
    best = scored[0]

    # --- apply best ---
    _, tag, code, analysis = best
    result = apply_safe_change(TARGET_FILE, code)

    run = {
        "status": result.get("status"),
        "chosen": tag,
        "analysis": analysis,
        "backup": result.get("backup")
    }
    record(run)
    return run

def run_loop(iterations: int = 5, delay: float = 1.0):
    history = []
    for _ in range(iterations):
        res = run_once()
        history.append(res)
        time.sleep(delay)
    return {"status": "loop_complete", "iterations": iterations, "history": history}

