import time
from datetime import datetime
from backend.app.engines import builder_engine, watcher_engine, execution_engine, executor_worker

RUN_LOG = []

def run(payload):
    cycles = payload.get("cycles", 1)
    results = []

    for i in range(cycles):
        cycle = {
            "cycle": i + 1,
            "time": datetime.utcnow().isoformat()
        }

        try:
            b = builder_engine.run({"limit": 3})
            w = watcher_engine.run({})
            e = execution_engine.run({})
            x = executor_worker.run({})

            cycle["builder"] = b.get("created_count", 0)
            cycle["executed"] = x.get("completed_count", 0)

        except Exception as e:
            cycle["error"] = str(e)

        results.append(cycle)
        time.sleep(1)

    return {
        "status": "autopilot_complete",
        "cycles": cycles,
        "results": results
    }