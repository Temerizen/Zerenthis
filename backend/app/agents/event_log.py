import sqlite3
import json
from typing import List, Dict
from backend.core.config import DB_PATH

def log_founder_event(event_type: str, payload: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO founder_events (event_type, payload) VALUES (?, ?)",
        (event_type, json.dumps(payload))
    )
    conn.commit()
    conn.close()

def get_founder_events(limit: int = 100) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, event_type, payload, created_at FROM founder_events ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

