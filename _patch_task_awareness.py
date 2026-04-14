from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")

old = 'chosen_task="execute_all",'
new = 'chosen_task=results[0].get("task", "unknown") if results else "no_task",'

if old in code:
    code = code.replace(old, new)
    p.write_text(code, encoding="utf-8")
    py_compile.compile(str(p), doraise=True)
    print("TASK-AWARE COGNITION ENABLED")
else:
    print("TARGET NOT FOUND")

