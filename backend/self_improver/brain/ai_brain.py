from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ROOT = Path(__file__).resolve().parents[3]
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SMARTER_SYSTEM_PROMPT = """
You are the Zerenthis self-improver brain.

Your job is to improve the system intelligently, not recklessly.

PRIORITIES:
1. Improve product quality and perceived value
2. Improve monetization readiness
3. Improve user flow and frontend usefulness
4. Improve reliability without endless duplicate safety tweaks
5. Improve automation in practical ways

AVOID:
- repeating the same 'harden/validate/safety' idea unless absolutely necessary
- touching core runtime files unless there is a very strong reason
- proposing cosmetic junk
- proposing vague ideas with no clear file actions
- proposing changes to .env, secrets, auth, billing, deploy, Railway, Vercel, or other critical infrastructure

PREFER:
- improving product_engine.py
- improving frontend-facing files
- improving metadata, output quality, CTA quality, offer structure
- improving gallery usefulness
- improving generated asset value
- adding helper files rather than breaking working files
- changes that make Zerenthis feel more premium, useful, and sellable

IMPORTANT:
Return only 1 to 2 proposals per cycle.
Each proposal must be realistic for the current repo.
Each proposal must use only these actions:
- create_file
- edit_file
- delete_file

For edit_file:
- use exact find text
- use exact replace text

Return ONLY valid JSON:
[
  {
    "title": "...",
    "reason": "...",
    "steps": [
      {
        "action": "edit_file",
        "path": "backend/Engine/product_engine.py",
        "find": "...",
        "replace": "..."
      }
    ]
  }
]
"""

def _safe_read(path: Path, limit: int = 7000) -> str:
    try:
        if not path.exists() or not path.is_file():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

def _repo_context() -> str:
    files = []
    targets = [
        ROOT / "backend" / "app" / "main.py",
        ROOT / "backend" / "self_improver" / "engine.py",
        ROOT / "backend" / "self_improver" / "worker.py",
        ROOT / "backend" / "Engine" / "product_engine.py",
        ROOT / "backend" / "Engine" / "video_engine.py",
        ROOT / "index.html",
    ]

    for target in targets:
        if target.exists():
            files.append(f"FILE: {target.relative_to(ROOT)}\n{_safe_read(target)}")

    tree_lines = []
    for base in [ROOT / "backend", ROOT]:
        if base.exists():
            for p in sorted(base.rglob("*")):
                if any(part in {".git", "__pycache__", "venv", "node_modules"} for part in p.parts):
                    continue
                if p.is_file():
                    rel = str(p.relative_to(ROOT)).replace("\\", "/")
                    tree_lines.append(rel)
                if len(tree_lines) >= 250:
                    break

    return (
        "REPO TREE SNAPSHOT:\n"
        + "\n".join(tree_lines[:250])
        + "\n\nKEY FILES:\n\n"
        + "\n\n".join(files)
    )

def _extract_json(text: str) -> Any:
    raw = text.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].strip()

    try:
        return json.loads(raw)
    except Exception:
        pass

    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        return json.loads(raw[start:end+1])

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        obj = json.loads(raw[start:end+1])
        return [obj]

    raise ValueError("Could not extract JSON from AI response")

def analyze_system() -> list[dict[str, Any]]:
    context = _repo_context()

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4"),
        instructions=SMARTER_SYSTEM_PROMPT,
        input=f"Analyze the current Zerenthis repo and propose the best next improvements.\n\n{context}",
    )

    text = getattr(response, "output_text", "") or ""
    data = _extract_json(text)

    if not isinstance(data, list):
        raise ValueError("AI output was not a list")

    cleaned: list[dict[str, Any]] = []
    for item in data[:2]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        reason = str(item.get("reason", "")).strip()
        steps = item.get("steps", [])
        if title and reason and isinstance(steps, list) and steps:
            cleaned.append({
                "title": title,
                "reason": reason,
                "steps": steps,
            })

    return cleaned
