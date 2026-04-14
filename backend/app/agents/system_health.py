import sqlite3
from backend.core.config import DB_PATH

def run_health_check():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        return True
    except Exception:
        return False

