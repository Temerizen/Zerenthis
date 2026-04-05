import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "genius")

def _slugify(value: str) -> str:
    value = (value or "genius_problem").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "genius_problem"

def create_genius_report(problem: str, mode: str = "theory", ambition: str = "high") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    now = datetime.now(timezone.utc)
    slug = _slugify(problem)
    filename = f"{slug}_{mode}_{int(now.timestamp())}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    content = f"""Zerenthis Genius Mode Report

Created: {now.isoformat()}
Problem: {problem}
Mode: {mode}
Ambition: {ambition}

Problem Framing:
Define the real question underneath the surface request.

Analysis Layers:
1. First-principles breakdown
2. Constraints
3. Hidden assumptions
4. Alternative models
5. Candidate solutions
6. Failure modes

Speculative Direction:
Generate a bold but testable path forward.

Next Move:
Turn the best candidate into an experiment plan.
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "status": "completed",
        "module": "genius",
        "file_name": filename,
        "file_url": f"/api/file/genius/{filename}"
    }
