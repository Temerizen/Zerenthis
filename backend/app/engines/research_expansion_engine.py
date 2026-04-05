import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "research")

def _slugify(value: str) -> str:
    value = (value or "research_pack").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "research_pack"

def create_research_pack(topic: str, depth: str = "standard") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    slug = _slugify(topic)
    bundle = f"{slug}_{depth}_{int(now.timestamp())}"
    bundle_dir = os.path.join(OUTPUT_DIR, bundle)
    os.makedirs(bundle_dir, exist_ok=True)

    files = {
        "research_brief.txt": f"Research brief for {topic}\n\nContext, key questions, and themes.\n",
        "hypotheses.txt": f"Hypotheses for {topic}\n\n1. Candidate hypothesis A\n2. Candidate hypothesis B\n",
        "comparison.txt": f"Comparison memo for {topic}\n\nApproach A vs Approach B.\n",
        "open_questions.txt": f"Open questions for {topic}\n\n- What is unknown?\n- What should be tested?\n",
        "experiment_plan.txt": f"Experiment plan for {topic}\n\nObjective, constraints, success criteria, next actions.\n"
    }

    for name, content in files.items():
        with open(os.path.join(bundle_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "status": "completed",
        "module": "research",
        "bundle": bundle,
        "files": [{"file_name": f"{bundle}/{k}", "file_url": f"/api/file/research/{bundle}/{k}"} for k in files.keys()]
    }
