from pathlib import Path

def run(payload):
    ROOT = Path(__file__).resolve().parents[3]
    path = ROOT / "backend/app/generated/live_build.py"

    path.parent.mkdir(parents=True, exist_ok=True)

    code = f"""
# AUTO-GENERATED
def system_status():
    return "Zerenthis is actively building at runtime"
"""

    path.write_text(code, encoding="utf-8")

    
    # === REAL BUILD TASKS ===
    if task.get("kind") == "create_file":
        return auto_file_write(task)

    if task.get("kind") == "append_file":
        return auto_append(task)

    if task.get("kind") == "ui":
        return auto_file_write(task)
 return {
        "status": "built",
        "file": str(path)
    }
