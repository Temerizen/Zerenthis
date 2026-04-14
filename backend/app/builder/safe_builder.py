import os
import shutil
import py_compile
import time
from typing import Dict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

BACKUP_DIR = os.path.join(BASE_DIR, "builder_backups")
os.makedirs(BACKUP_DIR, exist_ok=True)


def _backup_file(file_path: str) -> str:
    timestamp = str(int(time.time()))
    backup_path = os.path.join(BACKUP_DIR, f"{os.path.basename(file_path)}.{timestamp}.bak")
    shutil.copy(file_path, backup_path)
    return backup_path


def _validate_python(file_path: str) -> bool:
    try:
        py_compile.compile(file_path, doraise=True)
        return True
    except Exception as e:
        print(f"[BUILDER] Validation failed: {e}")
        return False


def apply_safe_change(file_path: str, new_code: str) -> Dict:
    if not os.path.exists(file_path):
        return {"status": "error", "reason": "file_not_found"}

    backup_path = _backup_file(file_path)

    temp_path = file_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    if not _validate_python(temp_path):
        os.remove(temp_path)
        return {
            "status": "rejected",
            "reason": "syntax_error",
            "backup": backup_path
        }

    shutil.move(temp_path, file_path)

    if not _validate_python(file_path):
        shutil.copy(backup_path, file_path)
        return {
            "status": "rolled_back",
            "reason": "post_apply_failure",
            "backup": backup_path
        }

    return {
        "status": "applied",
        "backup": backup_path
    }

