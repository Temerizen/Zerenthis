import sqlite3
from typing import List, Dict
from backend.core.config import DB_PATH

def log_education_run(run_type: str, subject: str, level: str, title: str, output_path: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO education_runs (run_type, subject, level, title, output_path) VALUES (?, ?, ?, ?, ?)",
        (run_type, subject, level, title, output_path)
    )
    conn.commit()
    conn.close()

def get_recent_education_runs(limit: int = 100) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, run_type, subject, level, title, output_path, created_at FROM education_runs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def log_cognitive_run(run_type: str, focus_area: str, title: str, output_path: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cognitive_runs (run_type, focus_area, title, output_path) VALUES (?, ?, ?, ?)",
        (run_type, focus_area, title, output_path)
    )
    conn.commit()
    conn.close()

def get_recent_cognitive_runs(limit: int = 100) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, run_type, focus_area, title, output_path, created_at FROM cognitive_runs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
