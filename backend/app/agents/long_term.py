import sqlite3
from typing import List, Dict, Any
from backend.core.config import DB_PATH

def save_long_term(category: str, content: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memory_items (category, content) VALUES (?, ?)",
        (category, content)
    )
    conn.commit()
    conn.close()

def recall_long_term(limit: int = 20, category: str | None = None) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if category:
        cur.execute(
            "SELECT id, category, content, created_at FROM memory_items WHERE category = ? ORDER BY id DESC LIMIT ?",
            (category, limit)
        )
    else:
        cur.execute(
            "SELECT id, category, content, created_at FROM memory_items ORDER BY id DESC LIMIT ?",
            (limit,)
        )

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

