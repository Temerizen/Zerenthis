from __future__ import annotations
import json, time, shutil, subprocess, hashlib
from pathlib import Path

PATH = Path("backend/data/apply_state.json")
VALIDATION_PATH = Path("backend/data/validation_state.json")

APPLY_ENABLED = True
CONFIDENCE_THRESHOLD = 0.65

SAFE_TARGETS = {
    "backend/app/cognition/explore.py",
    "backend/app/cognition/decision.py",
    "backend/app/cognition/planning.py",
}

def _default():
    return {
        "history": [],
        "applied": 0,
        "skipped": 0,
        "rolled_back": 0,
        "active_plan": None
    }

def _load():
    if not PATH.exists():
        return _default()
    try:
        return json.loads(PATH.read_text())
    except:
        return _default()

def _save(d):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(d, indent=2))

def _load_validation():
    if not VALIDATION_PATH.exists():
        return None
    try:
        return json.loads(VALIDATION_PATH.read_text())
    except:
        return None

def _hash_plan(plan):
    s = json.dumps({
        "target": plan["target"],
        "change": plan["change"]
    }, sort_keys=True)
    return hashlib.md5(s.encode()).hexdigest()

def _create_plan(proposal):
    plan = {
        "target": proposal["target"],
        "change": f"# improvement: {proposal['idea']}"
    }
    plan["plan_id"] = _hash_plan(plan)
    return plan

def _backup(file_path: str):
    src = Path(file_path)
    if not src.exists():
        return None

    backup_dir = Path("backend/builder_backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    dst = backup_dir / f"{src.name}.{int(time.time())}.bak"
    shutil.copy(src, dst)
    return str(dst)

def _post_compile(target):
    r = subprocess.run(["python","-m","py_compile",target],capture_output=True,text=True)
    if r.returncode != 0:
        return False, r.stderr[-400:]
    return True, ""

def _restore(target, backup):
    shutil.copy(backup, target)

def _apply(plan):
    if not APPLY_ENABLED:
        return {"status":"locked"}

    if plan["target"] not in SAFE_TARGETS:
        return {"status":"unsafe_target"}

    p = Path(plan["target"])
    if not p.exists():
        return {"status":"missing_target"}

    backup = _backup(plan["target"])
    if not backup:
        return {"status":"backup_failed"}

    content = p.read_text(encoding="utf-8",errors="ignore").lstrip("\ufeff")
    content += "\n" + plan["change"] + "\n"
    p.write_text(content,encoding="utf-8")

    ok, err = _post_compile(plan["target"])
    if not ok:
        _restore(plan["target"], backup)
        return {"status":"rollback","error":err}

    return {"status":"applied","backup":backup}

def _validation_passed(plan):
    v = _load_validation()
    if not v:
        return False

    last = v.get("last_result")
    if not last:
        return False

    validated_plan = last.get("plan")
    if not validated_plan:
        return False

    if validated_plan.get("target") != plan["target"]:
        return False
    if validated_plan.get("change") != plan["change"]:
        return False

    return last.get("validation",{}).get("valid",False)

def run(mod_state):
    state = _load()

    proposal = mod_state.get("proposal",{})
    accepted = mod_state.get("accepted",False)
    confidence = float(proposal.get("confidence",0))

    if not accepted:
        state["skipped"] += 1
        _save(state)
        return {"status":"not_accepted"}

    if confidence < CONFIDENCE_THRESHOLD:
        state["skipped"] += 1
        _save(state)
        return {"status":"low_confidence"}

    # --- LOCK PLAN ---
    if not state.get("active_plan"):
        state["active_plan"] = _create_plan(proposal)
        _save(state)
        return {"status":"plan_created","plan":state["active_plan"]}

    plan = state["active_plan"]

    # --- VALIDATION CHECK ---
    if not _validation_passed(plan):
        return {"status":"waiting_for_validation","plan":plan}

    # --- APPLY ---
    result = _apply(plan)

    state["history"].append({
        "t":time.time(),
        "plan":plan,
        "result":result
    })
    state["history"]=state["history"][-200:]
    state["active_plan"]=None

    if result["status"]=="applied":
        state["applied"]+=1
    elif result["status"]=="rollback":
        state["rolled_back"]+=1
    else:
        state["skipped"]+=1

    _save(state)

    return {"status":"applied_cycle","result":result}

def state():
    return _load()
