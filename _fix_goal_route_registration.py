from pathlib import Path
import py_compile

p = Path("backend/app/main.py")
code = p.read_text(encoding="utf-8")

# add import if missing
if "from backend.app.routes import goal_routes" not in code:
    lines = code.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, "from backend.app.routes import goal_routes")
    code = "\n".join(lines) + "\n"

# add router include if missing
if "app.include_router(goal_routes.router)" not in code:
    lines = code.splitlines()
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith("app = FastAPI("):
            new_lines.append("app.include_router(goal_routes.router)")
            inserted = True
    if not inserted:
        raise SystemExit("Could not find FastAPI app declaration in backend/app/main.py")
    code = "\n".join(new_lines) + "\n"

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)
print("GOAL_ROUTE_REGISTERED")
