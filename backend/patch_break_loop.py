from pathlib import Path
import shutil

main_path = Path("backend/app/main.py")
text = main_path.read_text(encoding="utf-8")

backup = main_path.with_suffix(".py.bak_loop_guard")
shutil.copy2(main_path, backup)

import_line = "from backend.app.cognition import loop_guard"
if import_line not in text:
    marker = "from backend.app.cognition.brain_context import load_brain_context"
    if marker in text:
        text = text.replace(marker, marker + "\n" + import_line, 1)
    else:
        text = import_line + "\n" + text

anchor = '        selected_task = selection_state.get("selected", {}) if isinstance(selection_state, dict) else {}'
insertion = '''        selected_task = selection_state.get("selected", {}) if isinstance(selection_state, dict) else {}

        loop_state = loop_guard.detect_loop(aux_pre["active_mission"])
        if loop_state.get("looping"):
            selected_task = {
                "task": loop_state.get("recommended_task", "advance_beyond_handoff"),
                "goal": loop_state.get("recommended_goal", "novel_progression"),
                "type": "loop_escape",
                "reason": loop_state.get("reason", "repeat_pair_detected"),
            }
            selection_state = {
                "status": "loop_override",
                "selected": selected_task,
                "loop_state": loop_state,
            }'''
if "loop_guard.detect_loop" not in text and anchor in text:
    text = text.replace(anchor, insertion, 1)

return_anchor = '            "continuity": continuity.get_state(),'
if '"loop_state": loop_state,' not in text and return_anchor in text:
    text = text.replace(
        return_anchor,
        '            "loop_state": loop_state,\n' + return_anchor,
        1
    )

main_path.write_text(text, encoding="utf-8", newline="\n")
print(f"PATCHED: {main_path}")
print(f"BACKUP:  {backup}")
