from __future__ import annotations
import json
import shutil
import time
from pathlib import Path
from backend.app.builder.policy_engine import assert_writable, load_policy
from backend.app.builder.validation_engine import validate_targets

BACKUP_ROOT = Path("backend/data/backups")
LOG_PATH = Path("backend/data/builder/apply_log.json")

def _load_log() -> list:
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    return []

def _save_log(items: list) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")

def _backup_file(path: Path) -> str | None:
    if not path.exists():
        return None
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = str(int(time.time() * 1000))
    dst = BACKUP_ROOT / f"{path.name}.{stamp}.bak"
    shutil.copy2(path, dst)
    return str(dst)

def apply_patch_plan(plan: dict) -> dict:
    changes = plan.get("changes", [])
    policy = load_policy()
    max_files = int(policy.get("max_files_per_apply", 2))

    if not isinstance(changes, list) or not changes:
        return {"status": "rejected", "reason": "no_changes"}

    if len(changes) > max_files:
        return {"status": "rejected", "reason": f"too_many_files>{max_files}"}

    backups: list[tuple[Path, str | None]] = []
    touched: list[str] = []

    try:
        for change in changes:
            path = Path(change["file"])
            content = change["content"]

            assert_writable(str(path))
            backup = _backup_file(path)
            backups.append((path, backup))

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            touched.append(str(path).replace("\\", "/"))

        ok, errors = validate_targets(touched)
        if not ok:
            for path, backup in backups:
                if backup:
                    shutil.copy2(backup, path)
            result = {
                "status": "rolled_back",
                "touched": touched,
                "errors": errors,
            }
        else:
            result = {
                "status": "applied",
                "touched": touched,
                "errors": [],
            }

    except Exception as e:
        for path, backup in backups:
            if backup:
                shutil.copy2(backup, path)
        result = {
            "status": "error",
            "touched": touched,
            "errors": [str(e)],
        }

    log = _load_log()
    log.append({
        "timestamp": int(time.time()),
        "result": result,
        "plan_summary": plan.get("summary", ""),
    })
    _save_log(log)
    return result

