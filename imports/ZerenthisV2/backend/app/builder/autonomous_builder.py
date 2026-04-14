import os
import time
import random
from typing import Dict

from backend.app.builder.builder_intelligence import analyze_change
from backend.app.builder.safe_builder import apply_safe_change

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

TARGET_FILE = os.path.join(BASE_DIR, "backend/app/test_file.py")

# --- Simple proposal generator (safe, small edits only) ---
def propose_change() -> Dict:
    # Tiny variations to avoid large diffs
    variants = [
        'print("DIFFERENT")',
        'print("DIFFERENT 1")',
        'print("DIFFERENT 2")',
        'print("OK")',
        'print("OK 1")'
    ]
    new_code = random.choice(variants) + "\n"
    return {
        "file_path": TARGET_FILE,
        "new_code": new_code,
        "reason": "tiny_variant"
    }


def run_once() -> Dict:
    if not os.path.exists(TARGET_FILE):
        return {"status": "error", "reason": "target_missing", "path": TARGET_FILE}

    # Read true current state
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        old_code = f.read()

    proposal = propose_change()

    analysis = analyze_change(TARGET_FILE, old_code, proposal["new_code"])

    if analysis.get("status") != "approved":
        return {
            "status": "skipped",
            "analysis": analysis,
            "proposal": proposal
        }

    result = apply_safe_change(TARGET_FILE, proposal["new_code"])

    return {
        "status": result.get("status"),
        "analysis": analysis,
        "proposal": proposal,
        "backup": result.get("backup")
    }


def run_loop(iterations: int = 5, delay: float = 1.0):
    history = []
    for i in range(iterations):
        res = run_once()
        history.append(res)
        time.sleep(delay)
    return {
        "status": "loop_complete",
        "iterations": iterations,
        "history": history
    }
