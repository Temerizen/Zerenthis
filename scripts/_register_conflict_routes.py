from pathlib import Path
import py_compile

p = Path("backend/app/main.py")
code = p.read_text(encoding="utf-8")

if "from backend.app.routes import conflict_routes" not in code:
    code = "from backend.app.routes import conflict_routes\n" + code

if "app.include_router(conflict_routes.router)" not in code:
    lines = code.splitlines()
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith("app = FastAPI("):
            new_lines.append("app.include_router(conflict_routes.router)")
    code = "\n".join(new_lines)

p.write_text(code, encoding="utf-8")
py_compile.compile(str(p), doraise=True)

print("CONFLICT_ROUTE_REGISTERED")
