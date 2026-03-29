from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.self_improver.worker import run_ai_cycle
from backend.self_improver.engine import pending, approve, execute, propose
from backend.self_improver.risk_engine import score_proposal, LOW, MEDIUM, HIGH
from backend.self_improver.decomposer import decompose_proposal
from backend.self_improver.mitigation_planner import build_mitigation_notes

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "backend" / "data" / "self_improver"
DATA_DIR.mkdir(parents=True, exist_ok=True)
AUTOPILOT_LOG = DATA_DIR / "autopilot_log.json"

def _load_log() -> list[dict]:
    if not AUTOPILOT_LOG.exists():
        return []
    try:
        return json.loads(AUTOPILOT_LOG.read_text(encoding="utf-8"))
    except Exception:
        return []

def _save_log(items: list[dict]) -> None:
    AUTOPILOT_LOG.write_text(json.dumps(items, indent=2), encoding="utf-8")

def _log(event: dict) -> None:
    items = _load_log()
    items.append(event)
    _save_log(items)

def _git_commit_and_push() -> None:
    if os.getenv("AUTO_PUSH", "true").lower() not in {"1", "true", "yes", "on"}:
        print("AUTO_PUSH disabled, skipping git push.")
        return

    branch = os.getenv("AUTO_COMMIT_BRANCH", "main")
    msg = f"autopilot: applied self-improver updates {int(time.time())}"

    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
        commit = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if commit.returncode != 0:
            print("Git commit skipped:", commit.stdout.strip() or commit.stderr.strip())
            return
        subprocess.run(["git", "push", "origin", branch], cwd=ROOT, check=True)
        print("Git push complete.")
    except Exception as e:
        print("Git push error:", e)

def _already_split_title(title: str) -> bool:
    t = title.lower()
    return "[safe-prep]" in t or "[approval-needed]" in t

def process_pending() -> None:
    items = pending()
    if not items:
        print("No pending proposals.")
        return

    for proposal in items:
        pid = proposal.get("id")
        title = proposal.get("title", "(untitled)")

        if _already_split_title(title):
            print(f"Leaving split proposal in queue: {pid} | {title}")
            continue

        score = score_proposal(proposal)
        risk = score["risk"]

        if risk == LOW:
            print(f"Auto-approving LOW risk: {pid} | {title}")
            approve(pid)
            result = execute(pid)
            print("Execution result:", result)
            _log({
                "time": int(time.time()),
                "id": pid,
                "title": title,
                "risk": risk,
                "result": result,
            })
            if result.get("ok"):
                _git_commit_and_push()
            continue

        if risk == MEDIUM:
            print(f"MEDIUM risk proposal detected: {pid} | {title}")
            parts = decompose_proposal(proposal)

            safe_part = parts.get("safe_proposal")
            risky_part = parts.get("risky_remainder")

            if safe_part and safe_part.get("steps"):
                try:
                    created = propose(safe_part["title"], safe_part["reason"], safe_part["steps"])
                    print("Created safe-prep proposal:", created.get("id"))
                except Exception as e:
                    print("Safe-prep creation failed:", e)

            if risky_part and risky_part.get("steps"):
                notes = build_mitigation_notes(risky_part)
                risky_reason = risky_part["reason"] + " | " + " ; ".join(notes["mitigation_notes"])
                try:
                    created = propose(risky_part["title"], risky_reason, risky_part["steps"])
                    print("Created approval-needed proposal:", created.get("id"))
                except Exception as e:
                    print("Remainder creation failed:", e)

            try:
                from backend.self_improver.engine import reject
                reject(pid)
            except Exception:
                pass

            _log({
                "time": int(time.time()),
                "id": pid,
                "title": title,
                "risk": risk,
                "result": "split_into_safe_and_risky",
            })
            continue

        if risk == HIGH:
            print(f"HIGH risk proposal detected: {pid} | {title}")
            parts = decompose_proposal(proposal)

            safe_part = parts.get("safe_proposal")
            risky_part = parts.get("risky_remainder")

            if safe_part and safe_part.get("steps"):
                try:
                    created = propose(safe_part["title"], safe_part["reason"], safe_part["steps"])
                    print("Created safe-prep proposal:", created.get("id"))
                except Exception as e:
                    print("Safe-prep creation failed:", e)

            if risky_part and risky_part.get("steps"):
                notes = build_mitigation_notes(risky_part)
                risky_reason = risky_part["reason"] + " | " + " ; ".join(notes["mitigation_notes"])
                try:
                    created = propose(risky_part["title"], risky_reason, risky_part["steps"])
                    print("Created approval-needed proposal:", created.get("id"))
                except Exception as e:
                    print("Remainder creation failed:", e)

            try:
                from backend.self_improver.engine import reject
                reject(pid)
            except Exception:
                pass

            _log({
                "time": int(time.time()),
                "id": pid,
                "title": title,
                "risk": risk,
                "result": "reduced_risk_and_queued_remainder",
            })

def run() -> None:
    interval = int(os.getenv("AUTOPILOT_INTERVAL_SECONDS", "120"))
    print("Autopilot started.")
    print("Interval:", interval, "seconds")
    while True:
        try:
            print("Running AI cycle...")
            run_ai_cycle()
            print("Processing pending proposals...")
            process_pending()
            print("Autopilot cycle complete.")
        except Exception as e:
            print("AUTOPILOT ERROR:", e)

        time.sleep(interval)

if __name__ == "__main__":
    run()
