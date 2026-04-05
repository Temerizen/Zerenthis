import time
from app.engines.builder_engine import run_builder
from app.engines.execution_engine import run_execution
from app.engines.money_engine import run_money
from app.engines.self_improver import run_self_improver

def run_core_loop():
    print("🚀 Zerenthis Core Loop Started")

    while True:
        try:
            print("🧠 Running Builder...")
            run_builder()

            print("⚙️ Running Execution...")
            run_execution()

            print("💰 Running Money Engine...")
            run_money()

            print("🧬 Running Self Improver...")
            run_self_improver()

        except Exception as e:
            print("Core Loop Error:", e)

        time.sleep(30)
