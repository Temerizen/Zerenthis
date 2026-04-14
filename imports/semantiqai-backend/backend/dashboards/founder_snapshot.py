import sqlite3
from backend.core.config import DB_PATH

def count_rows(table_name: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    result = cur.fetchone()[0]
    conn.close()
    return int(result)

def build_founder_snapshot() -> dict:
    return {
        "memory_items": count_rows("memory_items"),
        "prompt_runs": count_rows("prompt_runs"),
        "content_runs": count_rows("content_runs"),
        "education_runs": count_rows("education_runs"),
        "cognitive_runs": count_rows("cognitive_runs"),
        "simulation_runs": count_rows("simulation_runs"),
        "growth_runs": count_rows("growth_runs"),
        "founder_events": count_rows("founder_events")
    }
