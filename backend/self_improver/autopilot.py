from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.self_improver.worker import run_ai_cycle
from backend.self_improver.engine import pending, approve, execute

ROOT = Path(__file__).resolve().parents[2]

SAFE_PATH_PREFIXES = [
    "backend/self_improver/",
    "backend/Engine/product_engine.py",
    "backend/Engine/video_engine.py",
    "index.html",
]

BLOCKED_TOKENS = {
    ".env",
    ".git",
    "node_modules",
    "venv",
    "backend/data",
    "auth",
    "billing",
    "payment",
    "secret",
    "deploy",
    "railway",
    "vercel",
}

def _path_is_safe(path: str) -> bool:
    norm = path.replace("\\", "/").strip()
    if any(token in norm.lower() for token in BLOCKED_TOKENS):
        return False
    return any(norm.startswith(prefix) or norm == prefix for prefix in SAFE_PATH_PREFIXES)

def _proposal_is_safe(proposal: dict) -> tuple[bool, str]:
    steps = proposal.get("steps", [])
    if not isinstance(steps, list) or not steps:
        return False, "no steps"

    for step in steps:
        action = step.get("action")
        path = str(step.get("path", ""))
        if action not in {"create_file", "edit_file", "delete_file"}:
            return False, f"unsupported action: {action}"
        if not _path_is_safe(path):
            return False, f"unsafe path: {path}"
    return True, "safe"

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

def process_pending() -> None:
    items = pending()
    if not items:
        print("No pending proposals.")
        return

    for proposal in items:
        pid = proposal.get("id")
        title = proposal.get("title", "(untitled)")
        safe, reason = _proposal_is_safe(proposal)

        if not safe:
            print(f"Skipping risky proposal {pid}: {title} | {reason}")
            continue

        print(f"Auto-approving: {pid} | {title}")
        approve(pid)

        result = execute(pid)
        print("Execution result:", result)

        if result.get("ok"):
            _git_commit_and_push()

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
