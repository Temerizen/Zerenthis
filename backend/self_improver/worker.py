from __future__ import annotations

import json
import time
from pathlib import Path

from self_improver.brain.ai_brain import analyze_system
from self_improver.engine import load, propose, approve
from self_improver.policy import classify_proposal

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "backend" / "data" / "self_improver"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SEEN_FILE = DATA_DIR / "seen_ai_titles.json"

CORE_BLOCK_PATHS = {
    "backend/self_improver/engine.py",
    "backend/self_improver/worker.py",
    "backend/self_improver/autopilot.py",
    "backend/self_improver/policy.py",
    "backend/self_improver/brain/ai_brain.py",
    "backend/app/main.py",
}

def _load_seen():
    if not SEEN_FILE.exists():
        return set()
    try:
        data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {str(x).lower() for x in data}
    except Exception:
        pass
    return set()

def _save_seen(seen):
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2), encoding="utf-8")

def _existing_titles():
    titles = set()
    try:
        for item in load():
            title = str(item.get("title", "")).strip().lower()
            if title:
                titles.add(title)
    except Exception:
        pass
    return titles

def _is_similar(a, b):
    a = a.lower().strip()
    b = b.lower().strip()
    return a == b or a in b or b in a

def _valid_step(step):
    action = step.get("action")
    path = str(step.get("path", "")).replace("\\", "/").strip()
    if action not in {"create_file", "edit_file", "delete_file"}:
        return False
    if not path or path in CORE_BLOCK_PATHS:
        return False
    if any(token in path.lower() for token in [".env", ".git", "venv", "node_modules", "auth", "billing", "deploy", "railway", "vercel", "secret"]):
        return False
    if action == "edit_file":
        return isinstance(step.get("find"), str) and isinstance(step.get("replace"), str) and bool(step.get("find"))
    if action == "create_file":
        return isinstance(step.get("content", ""), str)
    return True

def run_ai_cycle():
    print("Self-improver: scanning for elegant wins...")
    seen = _load_seen()
    existing = _existing_titles()

    try:
        ideas = analyze_system()
        print(f"Magic brain returned {len(ideas)} proposal(s)")
    except Exception as e:
        print("AI ERROR:", e)
        return

    created = 0
    auto_approved = 0

    for idea in ideas:
        title = str(idea.get("title", "")).strip()
        reason = str(idea.get("reason", "")).strip()
        steps = idea.get("steps", [])
        if not title or not reason or not isinstance(steps, list) or not steps:
            continue
        if any(_is_similar(title, t) for t in existing) or any(_is_similar(title, s) for s in seen):
            print("Skipping duplicate/similar:", title)
            continue

        filtered_steps = [s for s in steps if isinstance(s, dict) and _valid_step(s)]
        if not filtered_steps:
            print("Skipping risky/invalid proposal:", title)
            continue

        policy = classify_proposal({"title": title, "reason": reason, "steps": filtered_steps})
        if policy["tier"] == "blocked":
            print("Blocked proposal:", title, "-", "; ".join(policy["reasons"]))
            continue

        try:
            result = propose(title, reason, filtered_steps, meta={"policy": policy})
            seen.add(title.lower())
            created += 1
            print("Created proposal:", result.get("id"), "-", title, "| tier:", policy["tier"])

            if policy.get("auto_approve"):
                approve(result["id"])
                auto_approved += 1
                print("Auto-approved low-risk proposal:", result["id"])

        except Exception as e:
            print("PROPOSAL ERROR:", title, "-", e)

    _save_seen(seen)
    print("Cycle complete. New proposals:", created, "| auto-approved:", auto_approved)

def run():
    print("Self-improver worker started.")
    while True:
        run_ai_cycle()
        print("Sleeping 120s...")
        time.sleep(120)

if __name__ == "__main__":
    run()

