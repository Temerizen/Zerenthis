import sqlite3
from typing import List, Dict
from backend.core.config import DB_PATH

def log_content_run(content_type: str, title: str, topic: str, output_path: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO content_runs (content_type, title, topic, output_path) VALUES (?, ?, ?, ?)",
        (content_type, title, topic, output_path)
    )
    conn.commit()
    conn.close()

def get_recent_content_runs(limit: int = 100) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, content_type, title, topic, output_path, created_at FROM content_runs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
