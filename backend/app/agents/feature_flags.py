from backend.db import get_db, now_iso


def is_enabled(flag_key: str) -> bool:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT enabled FROM feature_flags WHERE flag_key = ?", (flag_key,))
    row = cur.fetchone()
    conn.close()
    return bool(row["enabled"]) if row else False


def set_flag(flag_key: str, enabled: bool):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO feature_flags (flag_key, enabled, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(flag_key) DO UPDATE SET enabled = excluded.enabled, updated_at = excluded.updated_at
        """,
        (flag_key, 1 if enabled else 0, now_iso()),
    )
    conn.commit()
    conn.close()
