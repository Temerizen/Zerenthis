from pathlib import Path
from backend.core.config import GROWTH_PLAN_DIR
from backend.utils.files import slugify, timestamp
from backend.utils.writer import write_text_file
from backend.growth.growth_builder import build_growth_plan, render_growth_plan_markdown
import sqlite3
from backend.core.config import DB_PATH

def log_growth_run(growth_type: str, target: str, title: str, output_path: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO growth_runs (growth_type, target, title, output_path) VALUES (?, ?, ?, ?)",
        (growth_type, target, title, output_path)
    )
    conn.commit()
    conn.close()

def get_recent_growth_runs(limit: int = 100):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, growth_type, target, title, output_path, created_at FROM growth_runs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def generate_growth_plan(target: str, platform: str, cadence: str) -> dict:
    data = build_growth_plan(target, platform, cadence)
    filename = f"{timestamp()}_{slugify(target)}_{slugify(platform)}_growth_plan.md"
    output_path = write_text_file(Path(GROWTH_PLAN_DIR) / filename, render_growth_plan_markdown(data))
    log_growth_run("growth_plan", target, data["title"], output_path)
    return {"run_type": "growth_plan", "title": data["title"], "output_path": output_path}
