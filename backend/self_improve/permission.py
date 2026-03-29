import json
from pathlib import Path

POLICY_PATH = Path("backend/self_improve/policy.json")
policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def classify_patch(patch):
    files = patch.get("files", [])

    for file_path in files:
        if any(blocked in file_path for blocked in policy["forbidden_paths"]):
            return "BLOCKED"

    for file_path in files:
        if file_path in policy["approval_required_paths"]:
            return "NEEDS_APPROVAL"

    changed_lines = patch.get("changed_lines", 0)
    if changed_lines > policy["max_patch_lines"]:
        return "NEEDS_APPROVAL"

    return "AUTO"
