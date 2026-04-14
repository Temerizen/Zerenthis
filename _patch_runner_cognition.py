from __future__ import annotations

import re
import shutil
import sys
import time
from pathlib import Path

RUNNER = Path("execution/runner.py")
BACKUP = Path("_backup") / f"runner.py.bak.{int(time.time())}"

if not RUNNER.exists():
    print(f"ERROR: missing {RUNNER}")
    sys.exit(1)

text = RUNNER.read_text(encoding="utf-8")

if "cognition_influence" in text:
    print("Runner already appears patched. No changes made.")
    sys.exit(0)

original = text
shutil.copy2(RUNNER, BACKUP)

def add_import_block(src: str) -> str:
    if "from backend.app.cognition.self_influence import cognition_influence" in src:
        return src

    lines = src.splitlines()
    insert_at = 0

    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1

    lines.insert(insert_at, "from backend.app.cognition.self_influence import cognition_influence")
    return "\n".join(lines) + "\n"

def add_helpers(src: str) -> str:
    if "_zt_apply_cognition_to_candidates" in src:
        return src

    helper = """

def _zt_candidate_name(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ("task", "name", "id", "key", "title", "chosen_task"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return "unknown_task"


def _zt_apply_cognition_to_candidates(items):
    if not isinstance(items, list):
        return items

    for item in items:
        try:
            if isinstance(item, dict):
                base = float(item.get("score", 0.0) or 0.0)
                item["cognition_influence"] = cognition_influence(item)
                item["score"] = round(base + item["cognition_influence"], 4)
        except Exception:
            pass
    return items
"""
    return src.rstrip() + "\n" + helper + "\n"

def patch_common_scoring_patterns(src: str):
    patterns = []

    patterns.append((
        r'(?m)^(\s*)(\w+)\.sort\(\s*key\s*=\s*lambda\s+(\w+)\s*:\s*\3\.get\("score",\s*0(?:\.0)?\)\s*,\s*reverse\s*=\s*True\s*\)',
        lambda m: f'{m.group(1)}{m.group(2)} = _zt_apply_cognition_to_candidates({m.group(2)})\n{m.group(1)}{m.group(2)}.sort(key=lambda {m.group(3)}: {m.group(3)}.get("score", 0), reverse=True)'
    ))

    patterns.append((
        r'(?m)^(\s*)(\w+)\s*=\s*sorted\(\s*(\w+)\s*,\s*key\s*=\s*lambda\s+(\w+)\s*:\s*\4\.get\("score",\s*0(?:\.0)?\)\s*,\s*reverse\s*=\s*True\s*\)',
        lambda m: f'{m.group(1)}{m.group(3)} = _zt_apply_cognition_to_candidates({m.group(3)})\n{m.group(1)}{m.group(2)} = sorted({m.group(3)}, key=lambda {m.group(4)}: {m.group(4)}.get("score", 0), reverse=True)'
    ))

    patterns.append((
        r'(?m)^(\s*)for\s+(\w+)\s+in\s+(\w+):\s*\n(\s+)(\2)\["score"\]\s*=\s*(.+)$',
        lambda m: f'{m.group(1)}for {m.group(2)} in {m.group(3)}:\n{m.group(4)}{m.group(5)}["score"] = {m.group(6)}\n{m.group(4)}{m.group(5)}["cognition_influence"] = cognition_influence({m.group(5)})\n{m.group(4)}{m.group(5)}["score"] = round(float({m.group(5)}.get("score", 0.0) or 0.0) + float({m.group(5)}["cognition_influence"]), 4)'
    ))

    patterns.append((
        r'(?m)^(\s*)(return\s+max\(\s*(\w+)\s*,\s*key\s*=\s*lambda\s+(\w+)\s*:\s*\4\.get\("score",\s*0(?:\.0)?\)\s*\))',
        lambda m: f'{m.group(1)}{m.group(3)} = _zt_apply_cognition_to_candidates({m.group(3)})\n{m.group(1)}{m.group(2)}'
    ))

    count = 0
    out = src

    for pattern, repl in patterns:
        new_out, n = re.subn(pattern, repl, out, count=1)
        if n > 0:
            out = new_out
            count += n
            break

    return out, count

text = add_import_block(text)
text = add_helpers(text)
text, patched = patch_common_scoring_patterns(text)

if patched == 0:
    RUNNER.write_text(original, encoding="utf-8")
    print("ERROR: no supported scoring pattern found in execution/runner.py")
    print(f"Backup kept at: {BACKUP}")
    sys.exit(2)

RUNNER.write_text(text, encoding="utf-8")
print(f"Patched runner successfully. Backup at: {BACKUP}")
