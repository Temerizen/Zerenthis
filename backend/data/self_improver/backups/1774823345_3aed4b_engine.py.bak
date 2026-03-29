from __future__ import annotations

import json
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "backend" / "data" / "self_improver"
BACKUPS = DATA / "backups"
FILE = DATA / "proposals.json"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

PROTECTED = {".env", ".git", "node_modules", "venv", "backend/data"}
ALLOWED_ACTIONS = {"create_file", "edit_file", "delete_file"}


def load() -> list[dict[str, Any]]:
    if not FILE.exists():
        return []
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save(d: list[dict[str, Any]]) -> None:
    FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")


def new_id() -> str:
    return f"prop_{int(time.time())}_{uuid.uuid4().hex[:8]}"


def _normalize_path(path_str: str) -> Path:
    path = (ROOT / path_str).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        raise ValueError("path escapes repo")
    return path


def _is_blocked(path_str: str) -> bool:
    normalized = path_str.replace("\\", "/").strip("/")
    return any(normalized == item or normalized.startswith(item + "/") for item in PROTECTED)


def _validate_steps(steps: list[dict[str, Any]]) -> None:
    if not isinstance(steps, list) or not steps:
        raise ValueError("steps must be a non-empty list")

    for step in steps:
        if not isinstance(step, dict):
            raise ValueError("each step must be an object")

        action = step.get("action")
        path = step.get("path")

        if action not in ALLOWED_ACTIONS:
            raise ValueError(f"invalid action: {action}")
        if not isinstance(path, str) or not path.strip():
            raise ValueError("invalid path")
        if _is_blocked(path):
            raise ValueError(f"blocked path: {path}")

        _normalize_path(path)

        if action == "create_file":
            if not isinstance(step.get("content", ""), str):
                raise ValueError("create_file requires string content")

        if action == "edit_file":
            find_text = step.get("find")
            replace_text = step.get("replace")
            if not isinstance(find_text, str) or not isinstance(replace_text, str):
                raise ValueError("edit_file requires string find and replace")
            if not find_text:
                raise ValueError("edit_file find cannot be empty")


def propose(title: str, reason: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    title = title.strip()
    reason = reason.strip()
    if not title or not reason:
        raise ValueError("title and reason are required")

    _validate_steps(steps)

    p = {
        "id": new_id(),
        "title": title,
        "reason": reason,
        "steps": steps,
        "status": "pending",
        "created_at": time.time(),
    }
    d = load()
    d.append(p)
    save(d)
    return p


def approve(pid: str) -> bool:
    d = load()
    found = False
    for x in d:
        if x["id"] == pid:
            x["status"] = "approved"
            x["approved_at"] = time.time()
            found = True
    save(d)
    return found


def reject(pid: str) -> bool:
    d = load()
    found = False
    for x in d:
        if x["id"] == pid:
            x["status"] = "rejected"
            x["rejected_at"] = time.time()
            found = True
    save(d)
    return found


def backup(path: Path) -> Path | None:
    if not path.exists() or not path.is_file():
        return None
    b = BACKUPS / f"{int(time.time())}_{uuid.uuid4().hex[:6]}_{path.name}.bak"
    shutil.copy2(path, b)
    return b


def verify() -> bool:
    return True


def execute(pid: str) -> dict[str, Any]:
    d = load()
    p = next((x for x in d if x["id"] == pid), None)

    if not p:
        return {"ok": False, "error": "proposal not found"}
    if p["status"] != "approved":
        return {"ok": False, "error": "not approved"}

    _validate_steps(p.get("steps", []))

    backups: list[tuple[Path, Path]] = []
    created: list[Path] = []

    try:
        for s in p["steps"]:
            path = _normalize_path(s["path"])

            if s["action"] == "create_file":
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    b = backup(path)
                    if b:
                        backups.append((path, b))
                else:
                    created.append(path)
                path.write_text(s.get("content", ""), encoding="utf-8")

            elif s["action"] == "edit_file":
                if not path.exists():
                    raise FileNotFoundError(f"missing file: {s['path']}")
                original = path.read_text(encoding="utf-8", errors="ignore")
                find_text = s["find"]
                replace_text = s["replace"]

                if find_text not in original:
                    raise ValueError(f"find text not found in: {s['path']}")

                b = backup(path)
                if b:
                    backups.append((path, b))

                updated = original.replace(find_text, replace_text, 1)
                if updated == original:
                    raise ValueError(f"edit produced no change for: {s['path']}")

                path.write_text(updated, encoding="utf-8")

            elif s["action"] == "delete_file":
                if not path.exists():
                    raise FileNotFoundError(f"missing file: {s['path']}")
                b = backup(path)
                if b:
                    backups.append((path, b))
                path.unlink()

        if not verify():
            raise RuntimeError("verification failed")

        p["status"] = "applied"
        p["applied_at"] = time.time()
        save(d)
        return {"ok": True, "id": pid, "status": "applied"}

    except Exception as e:
        for orig, b in backups:
            try:
                shutil.copy2(b, orig)
            except Exception:
                pass
        for path in created:
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass

        p["status"] = "failed"
        p["failed_at"] = time.time()
        p["error"] = str(e)
        save(d)
        return {"ok": False, "id": pid, "status": "failed", "error": str(e)}


def pending() -> list[dict[str, Any]]:
    return [x for x in load() if x.get("status") == "pending"]
