import os
import sys
import time
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB_PATH = ROOT / "backend" / "data.db"

def generate_text_fallback(prompt: str) -> str:
    prompt = (prompt or "").strip()
    if not prompt:
        return "No prompt provided."

    try:
        from backend.ai_engine import generate_text as engine_generate_text
        result = engine_generate_text(prompt)
        if result:
            return str(result).strip()
    except Exception:
        pass

    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-5.4")
        if api_key:
            client = OpenAI(api_key=api_key)
            response = client.responses.create(model=model, input=prompt)
            text = getattr(response, "output_text", None)
            if text:
                return text.strip()
    except Exception as e:
        return f"[WORKER OPENAI ERROR] {e}"

    return "Worker fallback response: no AI engine module available, but queue system is alive."

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_pending_jobs(limit=3):
    conn = db()
    rows = conn.execute(
        "SELECT id, input FROM jobs WHERE status = 'pending' ORDER BY id ASC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows

def claim_job(job_id):
    conn = db()
    conn.execute(
        "UPDATE jobs SET status = 'processing' WHERE id = ? AND status = 'pending'",
        (job_id,)
    )
    conn.commit()
    changed = conn.execute("SELECT changes() AS c").fetchone()["c"]
    conn.close()
    return changed > 0

def finish_job(job_id, output):
    conn = db()
    conn.execute(
        "UPDATE jobs SET status = 'done', output = ? WHERE id = ?",
        (output, job_id)
    )
    conn.commit()
    conn.close()

def fail_job(job_id, error_text):
    conn = db()
    conn.execute(
        "UPDATE jobs SET status = 'failed', output = ? WHERE id = ?",
        (error_text, job_id)
    )
    conn.commit()
    conn.close()

def main():
    print("Async worker running...")
    print(f"DB: {DB_PATH}")
    while True:
        jobs = fetch_pending_jobs(limit=3)
        if not jobs:
            time.sleep(2)
            continue

        for job in jobs:
            job_id = job["id"]
            input_text = job["input"]

            if not claim_job(job_id):
                continue

            try:
                output = generate_text_fallback(input_text)
                finish_job(job_id, output)
                print(f"[DONE] job {job_id}")
            except Exception as e:
                fail_job(job_id, str(e))
                print(f"[FAILED] job {job_id}: {e}")

        time.sleep(1)

if __name__ == "__main__":
    main()

