from __future__ import annotations

import py_compile
import shutil
import time
from pathlib import Path
from typing import Dict, Any

BACKUP_DIR = Path("backend/builder_backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def safe_write_python(target_path: str, new_content: str) -> Dict[str, Any]:
    path = Path(target_path)
    if not path.exists():
        return {"status": "error", "reason": "target_not_found", "target": target_path}

    timestamp = str(int(time.time()))
    backup_path = BACKUP_DIR / f"{path.name}.{timestamp}.bak"
    shutil.copy2(path, backup_path)

    path.write_text(new_content, encoding="utf-8", newline="\n")

    try:
        py_compile.compile(str(path), doraise=True)
        return {
            "status": "ok",
            "target": str(path),
            "backup": str(backup_path),
            "compiled": True,
        }
    except Exception as e:
        shutil.copy2(backup_path, path)
        return {
            "status": "rolled_back",
            "target": str(path),
            "backup": str(backup_path),
            "error": str(e),
        }

def safe_patch_python(target_path: str, old_text: str, new_text: str) -> Dict[str, Any]:
    path = Path(target_path)
    if not path.exists():
        return {"status": "error", "reason": "target_not_found", "target": target_path}

    original = path.read_text(encoding="utf-8")
    if old_text not in original:
        return {
            "status": "error",
            "reason": "pattern_not_found",
            "target": target_path,
        }

    updated = original.replace(old_text, new_text, 1)
    return safe_write_python(target_path, updated)

if __name__ == "__main__":
    print({
        "status": "ok",
        "message": "builder_guardrails_ready",
        "functions": ["safe_write_python", "safe_patch_python"],
        "backup_dir": str(BACKUP_DIR)
    })
