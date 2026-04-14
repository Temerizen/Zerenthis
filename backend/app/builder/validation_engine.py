from __future__ import annotations
import py_compile
from pathlib import Path

def validate_python_file(path: str) -> tuple[bool, str | None]:
    try:
        py_compile.compile(path, doraise=True)
        return True, None
    except Exception as e:
        return False, str(e)

def validate_entrypoint() -> tuple[bool, str | None]:
    target = Path("backend/app/main.py")
    if not target.exists():
        return False, "canonical entrypoint missing: backend/app/main.py"
    return validate_python_file(str(target))

def validate_targets(paths: list[str]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for path in paths:
        if path.endswith(".py"):
            ok, err = validate_python_file(path)
            if not ok and err:
                errors.append(f"{path}: {err}")
    ok, err = validate_entrypoint()
    if not ok and err:
        errors.append(err)
    return len(errors) == 0, errors

