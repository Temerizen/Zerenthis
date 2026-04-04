from pathlib import Path
from backend.core.config import COGNITIVE_DRILL_DIR, COGNITIVE_REPORT_DIR
from backend.utils.files import slugify, timestamp
from backend.utils.writer import write_text_file
from backend.cognitive.drill_builder import build_cognitive_drill, render_cognitive_drill
from backend.cognitive.report_builder import build_cognitive_report, render_cognitive_report
from backend.education.run_log import log_cognitive_run

def generate_drill(focus_area: str, difficulty: str) -> dict:
    data = build_cognitive_drill(focus_area, difficulty)
    filename = f"{timestamp()}_{slugify(focus_area)}_{slugify(difficulty)}_drill.md"
    output_path = write_text_file(Path(COGNITIVE_DRILL_DIR) / filename, render_cognitive_drill(data))
    log_cognitive_run("drill", focus_area, data["title"], output_path)
    return {"run_type": "drill", "title": data["title"], "output_path": output_path}

def generate_report(goal: str, current_state: str, target_state: str) -> dict:
    data = build_cognitive_report(goal, current_state, target_state)
    filename = f"{timestamp()}_{slugify(goal)}_cognitive_report.md"
    output_path = write_text_file(Path(COGNITIVE_REPORT_DIR) / filename, render_cognitive_report(data))
    log_cognitive_run("report", goal, data["title"], output_path)
    return {"run_type": "report", "title": data["title"], "output_path": output_path}
