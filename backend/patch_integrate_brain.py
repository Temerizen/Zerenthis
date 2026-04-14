from pathlib import Path
import shutil
import sys

main_path = Path("backend/app/main.py")
if not main_path.exists():
    print("ERROR: backend/app/main.py not found")
    sys.exit(1)

text = main_path.read_text(encoding="utf-8")
backup = main_path.with_suffix(".py.bak_brain_context")
shutil.copy2(main_path, backup)

import_line = "from backend.app.cognition.brain_context import load_brain_context"
if import_line not in text:
    anchor = "from backend.app.cognition import ("
    if anchor in text:
        text = text.replace(anchor, import_line + "\n\n" + anchor, 1)
    else:
        text = import_line + "\n" + text

if "brain_context = load_brain_context()" not in text:
    target = 'def brain():'
    if target in text:
        text = text.replace(
            target,
            target + '\n    brain_context = load_brain_context()',
            1
        )
    else:
        print("ERROR: def brain(): not found")
        sys.exit(1)

return_anchor = '        "world_model": world_model_state'
if return_anchor in text and '"brain_context": brain_context' not in text:
    text = text.replace(
        return_anchor,
        '        "world_model": world_model_state,\n        "brain_context": brain_context',
        1
    )
else:
    alt_anchor = '        "world_model_state": world_model_state'
    if alt_anchor in text and '"brain_context": brain_context' not in text:
        text = text.replace(
            alt_anchor,
            '        "world_model_state": world_model_state,\n        "brain_context": brain_context',
            1
        )
    elif '"brain_context": brain_context' not in text:
        print("ERROR: Could not find return anchor for world_model")
        print(f"Backup created at: {backup}")
        sys.exit(1)

main_path.write_text(text, encoding="utf-8")
print(f"PATCHED: {main_path}")
print(f"BACKUP:  {backup}")
