from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")
original = code

# imports
if "from backend.app.cognition.thought_engine import generate_thought" not in code:
    code = code.replace(
        "import time",
        "import time\nfrom backend.app.cognition.thought_engine import generate_thought\nfrom backend.app.cognition.identity_engine import update_identity\nfrom backend.app.cognition.reflection_engine import run_reflection"
    )

# init cycle counter if missing
if "cycle_count = 0" not in code:
    code = code.replace(
        "running = True",
        "running = True\ncycle_count = 0"
    )

# increment cycle counter inside loop
if "cycle_count += 1" not in code:
    code = code.replace(
        "while running:",
        "while running:\n        cycle_count += 1"
    )

# inject cognition after execute_all()
marker = "execute_all()"
if marker in code and "generate_thought(" not in code:
    code = code.replace(
        marker,
        '''execute_all()

        try:
            thought = generate_thought(
                current_goal="autonomy_cycle",
                chosen_task="execute_all",
                result="success",
                reasoning="Completed autonomy execution cycle and recorded internal state.",
                reflection="Cycle completed; cognition layer updated."
            )
            update_identity(
                current_goal="autonomy_cycle",
                chosen_task="execute_all",
                result="success",
                goal_aligned=True
            )
            if cycle_count % 3 == 0:
                run_reflection(10)
        except Exception as cognition_error:
            print(f"[AUTONOMY][COGNITION] {cognition_error}")'''
    )

if code == original:
    print("NO_CHANGES_APPLIED")
else:
    p.write_text(code, encoding="utf-8")
    py_compile.compile(str(p), doraise=True)
    print("AUTONOMY LOOP COGNITION INTEGRATED")
