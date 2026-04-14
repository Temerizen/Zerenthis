from pathlib import Path
from backend.core.config import FOUNDER_REPORT_DIR, FOUNDER_NAME
from backend.utils.files import timestamp
from backend.utils.writer import write_text_file
from backend.dashboards.founder_snapshot import build_founder_snapshot

def generate_founder_report() -> dict:
    snapshot = build_founder_snapshot()
    title = f"{FOUNDER_NAME} founder report"
    lines = "\n".join([f"- {k}: {v}" for k, v in snapshot.items()])
    content = f"""# {title}

## System Snapshot
{lines}

## Interpretation
This report shows current run counts across the SemantiqAI stack.
Use it to track system growth and operational activity.
"""
    filename = f"{timestamp()}_founder_report.md"
    output_path = write_text_file(Path(FOUNDER_REPORT_DIR) / filename, content)
    return {"title": title, "output_path": output_path, "snapshot": snapshot}

