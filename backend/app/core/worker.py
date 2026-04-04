from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.self_improver.brain.ai_brain import analyze_system
from backend.self_improver.engine import load, propose

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "backend" / "data" / "self_improver"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SEEN_FILE = DATA_DIR / "seen_ai_titles.json"

BLOCK_TERMS = {
    "harden self-improver",
    "validation-friendly",
    "safer public health info",
    "safe rollback",
}

def _load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    try:
        data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {str(x).lower() for x in data}
    except Exception:
        pass
    return set()

def _save_seen(seen: set[str]) -> None:
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2), encoding="utf-8")

def _existing_titles() -> set[str]:
    titles = set()
    try:
        for item in load():
            title = str(item.get("title", "")).strip().lower()
            if title:
                titles.add(title)
    except Exception as e:
        print("LOAD ERROR:", e)
    return titles

def _valid_step(step: dict) -> bool:
    action = step.get("action")
    path = step.get("path")
    if action not in {"create_file", "edit_file", "delete_file"}:
        return False
    if not isinstance(path, str) or not path.strip():
        return False
    if action == "edit_file":
        return isinstance(step.get("find"), str) and isinstance(step.get("replace"), str) and bool(step.get("find"))
    if action == "create_file":
        return isinstance(step.get("content", ""), str)
    return True

def _is_similar(a: str, b: str) -> bool:
    a = a.lower().strip()
    b = b.lower().strip()
    return a == b or a in b or b in a

def _blocked_title(title: str) -> bool:
    t = title.lower()
    return any(term in t for term in BLOCK_TERMS)

def run_ai_cycle() -> None:
    print("Starting AI analysis...")
    seen = _load_seen()
    existing = _existing_titles()

    try:
        ideas = analyze_system()
        print(f"AI returned {len(ideas)} proposal(s)")
    except Exception as e:
        print("AI ERROR:", e)
        return

    created = 0

    for idea in ideas:
        title = str(idea.get("title", "")).strip()
        reason = str(idea.get("reason", "")).strip()
        steps = idea.get("steps", [])

        if not title or not reason or not isinstance(steps, list) or not steps:
            print("Skipping malformed idea")
            continue

        if _blocked_title(title):
            print("Skipping low-value repeat:", title)
            continue

        if any(_is_similar(title, t) for t in existing) or any(_is_similar(title, s) for s in seen):
            print("Skipping duplicate/similar:", title)
            continue

        filtered_steps = [s for s in steps if isinstance(s, dict) and _valid_step(s)]
        if not filtered_steps:
            print("Skipping invalid proposal:", title)
            continue

        try:
            result = propose(title, reason, filtered_steps)
            seen.add(title.lower())
            created += 1
            print("Created proposal:", result.get("id"), "-", title)
        except Exception as e:
            print("PROPOSAL ERROR:", title, "-", e)

    _save_seen(seen)
    print("AI cycle complete. New proposals:", created)

def run() -> None:
    print("Self-improver worker started.")
    while True:
        run_ai_cycle()
        time.sleep(30)

if __name__ == "__main__":
    run()
