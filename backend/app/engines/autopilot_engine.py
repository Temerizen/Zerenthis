import json
from backend.app.autonomy.memory import add, recent
from backend.app.autonomy.planner import plan
from backend.app.core.interpreter import interpret
from backend.app.engines.autonomous_executor import run as execute
from backend.app.autonomy.self_healer import fix_file

def run(payload):
    goal = payload.get("goal", "Improve Zerenthis system")

    mem = recent()

    tasks_json = plan(goal, mem)

    try:
        tasks = json.loads(tasks_json)
    except:
        tasks = [{"summary": goal}]

    results = []

    for t in tasks:
        task = interpret(t.get("summary", goal))
        result = execute({"task": task})

        file_path = result.get("file")
        if file_path:
            fix_file(file_path)

        add({
            "goal": goal,
            "task": task,
            "result": result
        })

        results.append(result)

    return {
        "status": "autopilot_cycle_complete",
        "tasks_executed": len(results),
        "results": results
    }