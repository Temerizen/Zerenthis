import os
import json
from datetime import datetime

PROPOSALS_PATH = "backend/data/self_surgeon_proposals.json"
BACKUP_PATH = "backend/data/self_surgeon_backups"

def now():
    return datetime.utcnow().isoformat()

def load_proposals():
    if not os.path.exists(PROPOSALS_PATH):
        return {"proposals": []}
    with open(PROPOSALS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_proposals(data):
    os.makedirs("backend/data", exist_ok=True)
    with open(PROPOSALS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# =========================
# OBSERVER
# =========================

def observe_system():
    issues = []

    try:
        with open("backend/app/evo_engine.py", "r", encoding="utf-8") as f:
            code = f.read()

        if "V2 V2" in code:
            issues.append("mutation_noise_detected")

        if "score = 5" in code:
            issues.append("weak_scoring_logic")

    except:
        issues.append("engine_read_error")

    return issues

# =========================
# DIAGNOSIS
# =========================

def diagnose(issue):
    if issue == "mutation_noise_detected":
        return {
            "fix": "clean_mutation_logic",
            "risk": "low"
        }

    if issue == "weak_scoring_logic":
        return {
            "fix": "improve_scoring_weights",
            "risk": "medium"
        }

    return {
        "fix": "unknown",
        "risk": "high"
    }

# =========================
# PROPOSAL CREATION
# =========================

def create_proposals():
    issues = observe_system()
    proposals = load_proposals()

    for issue in issues:
        diagnosis = diagnose(issue)

        proposal = {
            "id": str(len(proposals["proposals"]) + 1),
            "issue": issue,
            "fix": diagnosis["fix"],
            "risk": diagnosis["risk"],
            "status": "pending",
            "created_at": now()
        }

        proposals["proposals"].append(proposal)

    save_proposals(proposals)
    return proposals

# =========================
# SAFE PATCHES
# =========================

def backup_file(path):
    os.makedirs(BACKUP_PATH, exist_ok=True)
    backup_name = f"{BACKUP_PATH}/{os.path.basename(path)}_{int(datetime.utcnow().timestamp())}.bak"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    with open(backup_name, "w", encoding="utf-8") as f:
        f.write(content)
    return backup_name

def apply_fix(proposal):
    target = "backend/app/evo_engine.py"

    backup = backup_file(target)

    with open(target, "r", encoding="utf-8") as f:
        code = f.read()

    if proposal["fix"] == "clean_mutation_logic":
        code = code.replace("V2 V2", "V3")

    if proposal["fix"] == "improve_scoring_weights":
        code = code.replace("score = 5", "score = 6")

    with open(target, "w", encoding="utf-8") as f:
        f.write(code)

    return {
        "backup": backup,
        "status": "applied"
    }

# =========================
# VALIDATION
# =========================

def validate():
    try:
        import importlib
        import backend.app.evo_engine
        importlib.reload(app.evo_engine)
        return True
    except:
        return False

# =========================
# ROLLBACK
# =========================

def rollback(backup_path, target):
    with open(backup_path, "r", encoding="utf-8") as f:
        content = f.read()

    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

# =========================
# EXECUTION
# =========================

def run_surgeon():
    proposals = create_proposals()

    results = []

    for p in proposals["proposals"]:
        if p["status"] != "pending":
            continue

        if p["risk"] == "low":
            result = apply_fix(p)

            if validate():
                p["status"] = "applied"
            else:
                rollback(result["backup"], "backend/app/evo_engine.py")
                p["status"] = "failed"

            results.append(p)

    save_proposals(proposals)

    return {
        "processed": len(results),
        "details": results
    }

