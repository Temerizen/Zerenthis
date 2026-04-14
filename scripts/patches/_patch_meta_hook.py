from pathlib import Path
import re

path = Path(r"backend\app\execution\runner.py")
text = path.read_text(encoding="utf-8")

# 1. Ensure imports exist
if "from backend.app.core.goal_schema import enforce_goal_schema" not in text:
    text = text.replace(
        "import random",
        "import random\nfrom backend.app.core.goal_schema import enforce_goal_schema\nfrom backend.app.core.meta_intelligence import update_meta"
    )

# 2. Force schema normalization inside select_active_goal loop
text = re.sub(
    r"for goal in goals:\n",
    "for goal in goals:\n        goal = enforce_goal_schema(goal)\n        if goal is None:\n            continue\n",
    text,
    count=1
)

# 3. Force meta update right before return selected, ranked
pattern = r"return selected, ranked"
replacement = """try:
        update_meta(selected)
    except Exception as e:
        print(f"[META ERROR] {e}")
    return selected, ranked"""
text, count = re.subn(pattern, replacement, text, count=1)

if count != 1:
    raise SystemExit(f"Patch failed. return selected, ranked replacements: {count}")

path.write_text(text, encoding="utf-8")
print("Patched meta hook successfully.")
