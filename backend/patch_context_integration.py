from pathlib import Path
import shutil
import sys

main_path = Path("backend/app/main.py")
text = main_path.read_text(encoding="utf-8")

backup = main_path.with_suffix(".py.bak_context_fix")
shutil.copy2(main_path, backup)

# 1. Inject import
import_line = "from backend.app.cognition.brain_context import load_brain_context"
if import_line not in text:
    text = import_line + "\n" + text

# 2. Inject context load AFTER aux_pre
target_block = "aux_pre = _read_aux_state()"
if target_block in text and "brain_context = load_brain_context()" not in text:
    text = text.replace(
        target_block,
        target_block + "\n\n        brain_context = load_brain_context()",
        1
    )

# 3. Override goal/reflection BEFORE selection
override_block = """
        # Inject real context (override legacy aux)
        if isinstance(brain_context.get("goal_state"), dict):
            aux_pre["goal_state"] = brain_context["goal_state"]

        if isinstance(brain_context.get("reflection"), dict):
            aux_pre["reflection_state"] = brain_context["reflection"]
"""

if "Inject real context" not in text:
    text = text.replace(
        "selection_state = task_selection.select_next_task(",
        override_block + "\n        selection_state = task_selection.select_next_task(",
        1
    )

# 4. Add brain_context to final return
return_anchor = '"continuity": continuity.get_state(),'
if return_anchor in text and '"brain_context": brain_context' not in text:
    text = text.replace(
        return_anchor,
        return_anchor + '\n            "brain_context": brain_context,',
        1
    )

main_path.write_text(text, encoding="utf-8")

print("PATCHED successfully")
print(f"Backup at: {backup}")
