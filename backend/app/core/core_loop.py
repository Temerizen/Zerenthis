import time

def safe_import():
    try:
        from backend.app.engines.builder_engine import run_builder
    except Exception:
        run_builder = lambda: print("builder skipped")

    try:
        from backend.app.engines.execution_engine import run_execution
    except Exception:
        run_execution = lambda: print("execution skipped")

    try:
        from backend.app.engines.money_engine import run_money
    except Exception:
        run_money = lambda: print("money skipped")

    try:
        from backend.app.engines.self_improver import run_self_improver
    except Exception:
        run_self_improver = lambda: print("self improver skipped")

    return run_builder, run_execution, run_money, run_self_improver


def run_core_loop():
    print("Zerenthis Core Loop SAFE MODE")
    run_builder, run_execution, run_money, run_self_improver = safe_import()

    while True:
        try:
            run_builder()
            run_execution()
            run_money()
            run_self_improver()
        except Exception as e:
            print("Core Loop Error:", e)
        time.sleep(30)
