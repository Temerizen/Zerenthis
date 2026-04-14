from pathlib import Path
from backend.core.config import SIMULATION_SCENARIO_DIR
from backend.utils.files import slugify, timestamp
from backend.utils.writer import write_text_file
from backend.simulation.scenario_builder import build_scenario, render_scenario_markdown
import sqlite3
from backend.core.config import DB_PATH

def log_simulation_run(scenario_name: str, domain: str, title: str, output_path: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO simulation_runs (scenario_name, domain, title, output_path) VALUES (?, ?, ?, ?)",
        (scenario_name, domain, title, output_path)
    )
    conn.commit()
    conn.close()

def get_recent_simulation_runs(limit: int = 100):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, scenario_name, domain, title, output_path, created_at FROM simulation_runs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def generate_scenario(name: str, domain: str, objective: str, constraints: list[str]) -> dict:
    data = build_scenario(name, domain, objective, constraints)
    filename = f"{timestamp()}_{slugify(name)}_{slugify(domain)}_scenario.md"
    output_path = write_text_file(Path(SIMULATION_SCENARIO_DIR) / filename, render_scenario_markdown(data))
    log_simulation_run(name, domain, data["title"], output_path)
    return {"run_type": "simulation", "title": data["title"], "output_path": output_path}

