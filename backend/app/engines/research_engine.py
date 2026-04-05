import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "research")

def _slugify(value: str) -> str:
    value = (value or "research").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "research"

def create_research_brief(topic: str, audience: str = "general", depth: str = "standard") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    now = datetime.now(timezone.utc)
    slug = _slugify(topic)
    filename = f"{slug}_{depth}_{int(now.timestamp())}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    content = f"""Zerenthis Research Brief

Created: {now.isoformat()}
Topic: {topic}
Audience: {audience}
Depth: {depth}

Research Framing:
This brief explores {topic} for {audience} readers.

Sections:
1. Core question
2. Background context
3. Key themes
4. Important tensions
5. Open problems
6. Practical implications

Working Summary:
- What the topic is
- Why it matters
- What should be studied next
- Which assumptions need testing

Suggested Follow-Up:
Create a deeper synthesis, collect sources, compare competing viewpoints, and produce a decision memo.
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "status": "completed",
        "module": "research",
        "file_name": filename,
        "file_url": f"/api/file/research/{filename}"
    }
