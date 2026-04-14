from pathlib import Path
from datetime import datetime, timezone
from backend.app.core.codegen import generate_code

def run(payload):
    task = payload.get("task")

    prompt = f"""
You are an elite AI software engineer.

TASK:
{task.get("summary")}

TARGET FILE:
{task.get("target")}

Build FULL production-ready Python code.

Requirements:
- No placeholders
- Include imports
- Clean architecture
- Works immediately
"""

    code = generate_code(prompt)

    path = Path(task.get("target"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")

    return {
        "status": "code_generated",
        "file": str(path),
        "time": datetime.now(timezone.utc).isoformat()
    }
