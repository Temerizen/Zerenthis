import json
from backend.db import get_db, now_iso


def log_event(user_id: int, event_type: str, meta: dict | None = None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usage_events (user_id, event_type, meta_json, created_at) VALUES (?, ?, ?, ?)",
        (user_id, event_type, json.dumps(meta or {}), now_iso()),
    )
    conn.commit()
    conn.close()


def get_basic_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS n FROM users")
    users_total = cur.fetchone()["n"]

    cur.execute("SELECT COUNT(*) AS n FROM users WHERE role = 'founder'")
    founders_total = cur.fetchone()["n"]

    cur.execute("SELECT COUNT(*) AS n FROM users WHERE plan = 'pro'")
    pro_total = cur.fetchone()["n"]

    cur.execute("SELECT COUNT(*) AS n FROM users WHERE plan = 'free'")
    free_total = cur.fetchone()["n"]

    cur.execute("SELECT COUNT(*) AS n FROM history")
    messages_total = cur.fetchone()["n"]

    cur.execute("SELECT COUNT(*) AS n FROM jobs")
    jobs_total = cur.fetchone()["n"]

    cur.execute("SELECT COUNT(*) AS n FROM generated_assets")
    assets_total = cur.fetchone()["n"]

    conn.close()

    return {
        "users_total": users_total,
        "founders_total": founders_total,
        "pro_total": pro_total,
        "free_total": free_total,
        "messages_total": messages_total,
        "jobs_total": jobs_total,
        "assets_total": assets_total,
    }