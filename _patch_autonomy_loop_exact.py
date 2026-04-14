from pathlib import Path
import py_compile

p = Path("backend/app/autonomy/loop.py")
code = p.read_text(encoding="utf-8")
original = code

old = """            results = execute_all(limit=5)
            STATE["cycle_count"] += 1
            STATE["last_cycle_at"] = time.time()"""

new = """            results = execute_all(limit=5)
            STATE["cycle_count"] += 1
            STATE["last_cycle_at"] = time.time()

            try:
                generate_thought(
                    current_goal="autonomy_cycle",
                    chosen_task="execute_all",
                    result="success",
                    reasoning="Completed autonomy execution cycle and recorded internal state.",
                    reflection="Cycle completed; cognition layer updated.",
                    extra={"results": results, "cycle_count": STATE["cycle_count"]}
                )
                update_identity(
                    current_goal="autonomy_cycle",
                    chosen_task="execute_all",
                    result="success",
                    goal_aligned=True
                )
                if STATE["cycle_count"] % 3 == 0:
                    run_reflection(10)
            except Exception as cognition_error:
                print(f"[AUTONOMY][COGNITION] {cognition_error}")"""

if "generate_thought(" not in code and old in code:
    code = code.replace(old, new)

if code == original:
    print("NO_DIRECT_MATCH_FOUND")
else:
    p.write_text(code, encoding="utf-8")
    py_compile.compile(str(p), doraise=True)
    print("AUTONOMY_COGNITION_CALLS_PATCHED")
