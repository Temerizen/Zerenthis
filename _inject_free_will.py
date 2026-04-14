from pathlib import Path
import re

p = Path("backend/app/engines/decision_engine.py")
code = p.read_text(encoding="utf-8")

original = code

# 1. Ensure import
if "self_influence" not in code:
    code = code.replace(
        "from pathlib import Path",
        "from pathlib import Path\nfrom backend.app.cognition.self_influence import apply_self_influence"
    )

# 2. Inject into scoring loop
pattern = r'("score":\s*round\(final,\s*2\))'

if "apply_self_influence" not in code.split("score")[0]:
    code = re.sub(
        pattern,
        '''"score": round(
                apply_self_influence(name, final),
                2
            )''',
        code
    )

# 3. Write safely
p.write_text(code, encoding="utf-8")

# 4. Compile check
import py_compile
py_compile.compile(str(p), doraise=True)

print("SELF-INFLUENCE INTEGRATED INTO DECISION ENGINE")
