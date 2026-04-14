from pathlib import Path
import json
import os
import shutil

# --- create completion guard ---
guard_path = Path("backend/app/cognition/completion_guard.py")
guard_path.parent.mkdir(parents=True, exist_ok=True)
guard_code = r'''from __future__ import annotations

import json
import os
from typing import Any, Dict

COMPLETED_PATH = "backend/data/autonomy/completed_tasks.json"

def _load() -> Dict[str, Any]:
    if not os.path.exists(COMPLETED_PATH):
        return {}
    try:
        with open(COMPLETED_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(COMPLETED_PATH), exist_ok=True)
    with open(COMPLETED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_completed(task: str) -> bool:
    data = _load()
    item = data.get(task, {})
    return bool(item.get("completed", False)) if isinstance(item, dict) else bool(item)

def mark_completed(task: str, route: str = "", goal: str = "") -> Dict[str, Any]:
    data = _load()
    data[task] = {
        "completed": True,
        "route": route,
        "goal": goal,
    }
    _save(data)
    return data[task]
'''
guard_path.write_text(guard_code, encoding="utf-8", newline="\n")

# --- patch main.py safely ---
main_path = Path("backend/app/main.py")
backup = Path("backend/app/main.py.bak_completion_guard")
text = main_path.read_text(encoding="utf-8", errors="replace")
shutil.copy2(main_path, backup)

# hard-clean any BOM/junk and fix __future__ placement
text = text.replace("\ufeff", "").replace("ï»¿", "")
lines = text.splitlines()
lines = [ln for ln in lines if ln.strip() != "from __future__ import annotations"]
text = "\n".join(["from __future__ import annotations"] + lines) + "\n"

import_line = "from backend.app.cognition.completion_guard import is_completed, mark_completed"
if import_line not in text:
    marker = "from backend.app.cognition.brain_context import load_brain_context"
    if marker in text:
        text = text.replace(marker, marker + "\n" + import_line, 1)
    else:
        text = import_line + "\n" + text

# inject completion guard state before world/execution calls
anchor = '        selected_goal = selected_task.get("goal", "balanced_progression")'
inject = r'''        selected_goal = selected_task.get("goal", "balanced_progression")

        completion_guard_state = {
            "checked_task": selected_task_name,
            "was_completed": is_completed(selected_task_name),
            "override_applied": False,
        }

        if completion_guard_state["was_completed"] and selected_task_name in {"create_thought_engine", "resolve_builder_handoff"}:
            selected_task_name = "advance_beyond_handoff"
            selected_goal = "novel_progression"
            selected_task = {
                "task": selected_task_name,
                "goal": selected_goal,
                "type": "completion_guard",
                "reason": "task_already_completed",
            }
            selection_state = {
                "status": "completion_guard_override",
                "selected": selected_task,
                "completion_guard": completion_guard_state,
            }
            completion_guard_state["override_applied"] = True
            completion_guard_state["override_task"] = selected_task_name
'''
if 'completion_guard_state = {' not in text and anchor in text:
    text = text.replace(anchor, inject, 1)

# mark completed after successful execution
exec_anchor = '        execution_state = execution.run_execution(planning_state)'
exec_inject = r'''        execution_state = execution.run_execution(planning_state)

        if isinstance(execution_state, dict) and execution_state.get("status") == "execution_complete":
            completion_guard_state["marked_completed"] = mark_completed(
                selected_task_name,
                route=str(execution_state.get("route", "")),
                goal=str(selected_goal),
            )
'''
if 'completion_guard_state["marked_completed"]' not in text and exec_anchor in text:
    text = text.replace(exec_anchor, exec_inject, 1)

# return completion guard state in API output
ret_anchor = '            "continuity": continuity.get_state(),'
if '"completion_guard": completion_guard_state,' not in text and ret_anchor in text:
    text = text.replace(ret_anchor, '            "completion_guard": completion_guard_state,\n' + ret_anchor, 1)

main_path.write_text(text, encoding="utf-8", newline="\n")
print(f"PATCHED: {main_path}")
print(f"BACKUP:  {backup}")
