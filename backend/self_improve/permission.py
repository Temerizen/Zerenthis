import json

policy = json.load(open("backend/self_improve/policy.json"))

def classify_patch(patch):
    paths = patch.get("files", [])

    for p in paths:
        if any(x in p for x in policy["forbidden_paths"]):
            return "BLOCKED"

    if any(p in policy["approval_required_paths"] for p in paths):
        return "NEEDS_APPROVAL"

    return "AUTO"
