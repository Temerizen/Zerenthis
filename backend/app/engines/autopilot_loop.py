import time
from backend.app.engines import builder_engine, executor_worker

def run(payload):
    cycles = payload.get("cycles",5)
    results = []

    for i in range(cycles):
        b = builder_engine.run({})
        e = executor_worker.run({})

        results.append({
            "cycle": i,
            "built": b.get("created"),
            "executed": e.get("count")
        })

        time.sleep(1)

    return {"status":"autopilot_done","cycles":results}
