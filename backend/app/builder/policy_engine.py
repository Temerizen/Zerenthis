from __future__ import annotations
import json
from pathlib import Path

POLICY_PATH = Path("backend/data/builder/builder_policy.json")

def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8-sig"))

def _norm(path: str) -> str:
    return Path(path).as_posix().strip("/")

def _is_under(path: str, root: str) -> bool:
    p = _norm(path)
    r = _norm(root)
    return p == r or p.startswith(r + "/")

def path_status(path: str) -> str:
    policy = load_policy()
    p = _norm(path)

    for root in policy.get("denied_roots", []):
        if _is_under(p, root):
            return "denied"

    for root in policy.get("allowed_write_roots", []):
        if _is_under(p, root):
            return "allowed"

    for root in policy.get("read_only_roots", []):
        if _is_under(p, root):
            return "read_only"

    return "unknown"

def assert_writable(path: str) -> None:
    status = path_status(path)
    if status != "allowed":
        raise PermissionError(f"Builder cannot write to '{path}' (status={status})")


