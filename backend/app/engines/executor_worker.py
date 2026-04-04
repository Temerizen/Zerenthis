from pathlib import Path
from datetime import datetime, timezone
from backend.app.core.codegen import generate_code

def apply_task(task):
    target = task.get("target") or "backend/app/generated/auto.py"
    summary = task.get("summary", "Build feature")

    prompt = f"""
You are an elite AI engineer.

TASK:
{summary}

TARGET FILE:
{target}

Return FULL working Python code.
No placeholders.
Production ready.
"""

    code = generate_code(prompt)

    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")

    from backend.app.core.validator import validate
    ok = validate(str(path))
    return {
        "applied": True,
        "file": str(path),
        "action": "code_generated"
    }

def run(payload):
    import json
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[3]
    QUEUE = ROOT / "backend/data/execution/queue.json"

    try:
        queue = json.loads(QUEUE.read_text())
    except:
        from backend.app.core.validator import validate
    ok = validate(str(path))
    return {"status":"no_queue"}

    results = []

    for task in queue:
        if task.get("status") != "queued":
            continue

        res = apply_task(task)
        task["status"] = "completed"
        task["result"] = res
        results.append(res)

    QUEUE.write_text(json.dumps(queue, indent=2))

    from backend.app.core.validator import validate
    ok = validate(str(path))
    return {
        "status":"REAL_EXECUTION_COMPLETE",
        "built": len(results),
        "results": results
    }
