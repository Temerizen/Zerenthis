import os
import json
import sqlite3
import datetime

DB = os.path.join(os.path.dirname(__file__), "data.db")

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init():
    conn = connect()
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        agent TEXT NOT NULL,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS memory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mem_key TEXT NOT NULL,
        mem_value TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(user_id, mem_key),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        task_type TEXT NOT NULL,
        status TEXT NOT NULL,
        input_text TEXT NOT NULL,
        output_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS artifacts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        artifact_type TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS knowledge(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        source_type TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        is_read INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS request_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        path TEXT NOT NULL,
        method TEXT NOT NULL,
        status_code INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS profiles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        display_name TEXT,
        bio TEXT,
        goals_json TEXT NOT NULL DEFAULT '{}',
        onboarding_state TEXT NOT NULL DEFAULT 'new',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS plan_placeholders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_name TEXT NOT NULL DEFAULT 'free',
        usage_limit INTEGER NOT NULL DEFAULT 100,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

def save_history(uid, agent, msg, res):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO history(user_id, agent, message, response, created_at) VALUES (?, ?, ?, ?, ?)",
        (uid, agent, msg, res, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_history(uid, limit=30):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, agent, message, response, created_at FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (uid, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_user_by_username(username):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_by_id(uid):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, username, role, created_at FROM users WHERE id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    return row

def create_user(username, password_hash, role="user"):
    now = datetime.datetime.utcnow().isoformat()
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users(username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
        (username, password_hash, role, now)
    )
    uid = c.lastrowid
    c.execute(
        "INSERT INTO profiles(user_id, display_name, bio, goals_json, onboarding_state, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (uid, username, "", "{}", "new", now, now)
    )
    c.execute(
        "INSERT INTO plan_placeholders(user_id, plan_name, usage_limit, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (uid, "free", 100, now, now)
    )
    conn.commit()
    conn.close()
    return uid

def set_memory(uid, key, value):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO memory(user_id, mem_key, mem_value, updated_at) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(user_id, mem_key) DO UPDATE SET mem_value=excluded.mem_value, updated_at=excluded.updated_at",
        (uid, key, json.dumps(value, ensure_ascii=False), datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_memory(uid):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT mem_key, mem_value, updated_at FROM memory WHERE user_id = ?", (uid,))
    rows = c.fetchall()
    conn.close()
    out = {}
    for r in rows:
        try:
            out[r["mem_key"]] = json.loads(r["mem_value"])
        except Exception:
            out[r["mem_key"]] = r["mem_value"]
    return out

def create_task(uid, title, task_type, status, input_text, output_obj):
    now = datetime.datetime.utcnow().isoformat()
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks(user_id, title, task_type, status, input_text, output_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (uid, title, task_type, status, input_text, json.dumps(output_obj, ensure_ascii=False), now, now)
    )
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return task_id

def update_task(task_id, status, output_obj):
    now = datetime.datetime.utcnow().isoformat()
    conn = connect()
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET status = ?, output_json = ?, updated_at = ? WHERE id = ?",
        (status, json.dumps(output_obj, ensure_ascii=False), now, task_id)
    )
    conn.commit()
    conn.close()

def get_tasks(uid, limit=25):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, task_type, status, input_text, output_json, created_at, updated_at FROM tasks WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (uid, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def save_artifact(uid, title, artifact_type, filename, file_path):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO artifacts(user_id, title, artifact_type, filename, file_path, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (uid, title, artifact_type, filename, file_path, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_artifacts(uid, limit=100):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, artifact_type, filename, file_path, created_at FROM artifacts WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (uid, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def add_knowledge(uid, title, content, source_type="manual"):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO knowledge(user_id, title, content, source_type, created_at) VALUES (?, ?, ?, ?, ?)",
        (uid, title, content, source_type, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    kid = c.lastrowid
    conn.close()
    return kid

def get_knowledge(uid, limit=100):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, content, source_type, created_at FROM knowledge WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (uid, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def search_knowledge(uid, query, limit=10):
    conn = connect()
    c = conn.cursor()
    like = f"%{query}%"
    c.execute(
        "SELECT id, title, content, source_type, created_at FROM knowledge WHERE user_id = ? AND (title LIKE ? OR content LIKE ?) ORDER BY id DESC LIMIT ?",
        (uid, like, like, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def set_setting(key, value):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO settings(setting_key, setting_value, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value, updated_at=excluded.updated_at",
        (key, json.dumps(value, ensure_ascii=False), datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_settings():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT setting_key, setting_value, updated_at FROM settings")
    rows = c.fetchall()
    conn.close()
    out = {}
    for r in rows:
        try:
            out[r["setting_key"]] = json.loads(r["setting_value"])
        except Exception:
            out[r["setting_key"]] = r["setting_value"]
    return out

def add_notification(uid, title, body):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO notifications(user_id, title, body, is_read, created_at) VALUES (?, ?, ?, 0, ?)",
        (uid, title, body, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_notifications(uid, limit=50):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, body, is_read, created_at FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (uid, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def log_request(uid, path, method, status_code):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO request_logs(user_id, path, method, status_code, created_at) VALUES (?, ?, ?, ?, ?)",
        (uid, path, method, status_code, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_profile(uid):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT user_id, display_name, bio, goals_json, onboarding_state, created_at, updated_at FROM profiles WHERE user_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_profile(uid, display_name, bio, goals_json, onboarding_state):
    now = datetime.datetime.utcnow().isoformat()
    conn = connect()
    c = conn.cursor()
    c.execute(
        "UPDATE profiles SET display_name = ?, bio = ?, goals_json = ?, onboarding_state = ?, updated_at = ? WHERE user_id = ?",
        (display_name, bio, goals_json, onboarding_state, now, uid)
    )
    conn.commit()
    conn.close()

def get_plan_placeholder(uid):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT user_id, plan_name, usage_limit, created_at, updated_at FROM plan_placeholders WHERE user_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def admin_stats():
    conn = connect()
    c = conn.cursor()
    counts = {}
    for table in ["users", "history", "tasks", "artifacts", "knowledge", "notifications", "request_logs", "profiles", "plan_placeholders"]:
        c.execute(f"SELECT COUNT(*) AS n FROM {table}")
        counts[table] = c.fetchone()["n"]
    conn.close()
    return counts

def admin_users(limit=100):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, username, role, created_at FROM users ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def admin_tasks(limit=100):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, user_id, title, task_type, status, created_at, updated_at FROM tasks ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def admin_artifacts(limit=200):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, user_id, title, artifact_type, filename, file_path, created_at FROM artifacts ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def admin_knowledge(limit=200):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, user_id, title, source_type, created_at FROM knowledge ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def admin_request_logs(limit=200):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, user_id, path, method, status_code, created_at FROM request_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

