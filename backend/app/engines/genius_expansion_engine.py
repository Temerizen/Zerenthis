import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "genius")

def _slugify(value: str) -> str:
    value = (value or "genius_pack").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "genius_pack"

def create_breakthrough_pack(problem: str, mode: str = "theory") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    slug = _slugify(problem)
    bundle = f"{slug}_{mode}_{int(now.timestamp())}"
    bundle_dir = os.path.join(OUTPUT_DIR, bundle)
    os.makedirs(bundle_dir, exist_ok=True)

    files = {
        "problem_breakdown.txt": f"Problem breakdown for {problem}\n\nFirst principles, constraints, hidden assumptions.\n",
        "solution_space.txt": f"Solution space for {problem}\n\nCandidate directions and tradeoffs.\n",
        "theory_notes.txt": f"Theory notes for {problem}\n\nSpeculative but testable pathways.\n",
        "experiment_design.txt": f"Experiment design for {problem}\n\nTest plan, variables, success criteria.\n",
        "decision_memo.txt": f"Decision memo for {problem}\n\nBest next move and why.\n"
    }

    for name, content in files.items():
        with open(os.path.join(bundle_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "status": "completed",
        "module": "genius",
        "bundle": bundle,
        "files": [{"file_name": f"{bundle}/{k}", "file_url": f"/api/file/genius/{bundle}/{k}"} for k in files.keys()]
    }

