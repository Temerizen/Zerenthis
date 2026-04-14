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

def _safe_read(path: Path, limit: int = 6000) -> str:
    try:
        if not path.exists() or not path.is_file():
            return ""
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:limit]
    except Exception:
        return ""

def _repo_context() -> str:
    files = []

    targets = [
        ROOT / "backend" / "app" / "main.py",
        ROOT / "backend" / "self_improver" / "engine.py",
        ROOT / "backend" / "self_improver" / "routes.py",
        ROOT / "backend" / "Engine" / "product_engine.py",
        ROOT / "backend" / "Engine" / "video_engine.py",
    ]

    for target in targets:
        if target.exists():
            files.append(f"FILE: {target.relative_to(ROOT)}\n{_safe_read(target)}")

    # light repo tree snapshot
    tree_lines = []
    for base in [ROOT / "backend", ROOT / "frontend"]:
        if base.exists():
            for p in sorted(base.rglob("*")):
                rel = p.relative_to(ROOT)
                if any(part in {".git", "__pycache__", "venv", "node_modules"} for part in p.parts):
                    continue
                if p.is_file():
                    tree_lines.append(str(rel).replace("\\", "/"))
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

    if raw.startswith("`"):
        raw = raw.strip("")
        if raw.startswith("json"):
            raw = raw[4:].strip()

    # direct parse
    try:
        return json.loads(raw)
    except Exception:
        pass

    # try array slice
    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        return json.loads(raw[start:end+1])

    # try object slice
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(raw[start:end+1])

    raise ValueError("Could not extract JSON from AI response")

def analyze_system() -> list[dict[str, Any]]:
    context = _repo_context()

    prompt = f'''
You are an elite software architect improving a local AI product system named Zerenthis.

Your job:
Propose 1 to 3 HIGH-IMPACT improvements for this codebase.

Goals:
- improve self-improver quality
- improve product output quality
- improve monetization readiness
- improve reliability
- improve user flow

Rules:
- prefer editing existing files over creating many new ones
- only propose changes that are realistic for this repo
- every proposal must be approval-safe
- every proposal must use actions from this set only:
  create_file, edit_file, delete_file

For edit_file actions:
- include exact "find" text that should exist
- include exact "replace" text

For create_file actions:
- include full "content"

Return ONLY valid JSON as an array:
[
  {{
    "title": "Short title",
    "reason": "Why this matters",
    "steps": [
      {{
        "action": "edit_file",
        "path": "backend/app/main.py",
        "find": "old text",
        "replace": "new text"
      }}
    ]
  }}
]

Here is the repo context:

{context}
'''

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.3"),
        input=prompt,
    )

    text = getattr(response, "output_text", "") or ""
    data = _extract_json(text)

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("AI output was not a list of proposals")

    cleaned: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        reason = str(item.get("reason", "")).strip()
        steps = item.get("steps", [])
        if not title or not reason or not isinstance(steps, list) or not steps:
            continue
        cleaned.append({
            "title": title,
            "reason": reason,
            "steps": steps,
        })

    return cleaned

