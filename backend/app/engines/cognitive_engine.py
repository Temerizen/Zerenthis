import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "cognitive")

def _slugify(value: str) -> str:
    value = (value or "cognitive_session").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "cognitive_session"

def create_cognitive_session(focus: str, intensity: str = "medium", duration_minutes: int = 20) -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    now = datetime.now(timezone.utc)
    slug = _slugify(focus)
    filename = f"{slug}_{intensity}_{int(now.timestamp())}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    content = f"""Zerenthis Cognitive Lab Session

Created: {now.isoformat()}
Focus: {focus}
Intensity: {intensity}
Duration Minutes: {duration_minutes}

Session Structure:
1. Warm-up
2. Focus drill
3. Recall drill
4. Abstraction drill
5. Reflection

Exercises:
- Summarize a concept from memory
- Reframe it in simpler language
- Rebuild it in more advanced language
- Connect it to a second idea
- Reflect on what felt difficult

Target Outcome:
Improve structured thinking, recall, and mental flexibility around {focus}.
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "status": "completed",
        "module": "cognitive",
        "file_name": filename,
        "file_url": f"/api/file/cognitive/{filename}"
    }
