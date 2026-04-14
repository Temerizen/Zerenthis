from pathlib import Path

p = Path("backend/app/main.py")
code = p.read_text(encoding="utf-8")

if "from backend.app.routes import goal_routes" not in code:
    lines = code.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, "from backend.app.routes import goal_routes")
    code = "\n".join(lines) + "\n"

if "app.include_router(goal_routes.router)" not in code:
    marker = "app = FastAPI()"
    if marker in code:
        code = code.replace(marker, marker + "\napp.include_router(goal_routes.router)")
    else:
        raise SystemExit("Could not find app = FastAPI() in backend/app/main.py")

p.write_text(code, encoding="utf-8")
print("MAIN_PATCHED_FOR_GOALS")
