from pathlib import Path
import json, time

QUEUE_PATH = "backend/data/task_queue.json"

def load_queue():
    if Path(QUEUE_PATH).exists():
        return json.load(open(QUEUE_PATH, "r", encoding="utf-8"))
    return []

def save_queue(q):
    json.dump(q, open(QUEUE_PATH, "w", encoding="utf-8"), indent=2)

def process_next_task():
    queue = load_queue()

    for task in queue:
        if task.get("status") == "pending":
            task["status"] = "done"
            task["completed_at"] = time.time()

            save_queue(queue)

            return {
                "status": "executed",
                "task": task
            }

    return {"status": "idle"}

def run_loop(max_cycles=5, delay_seconds=0.5):
    results = []

    for _ in range(max_cycles):
        result = process_next_task()
        results.append(result)

        if result["status"] == "idle":
            break

        time.sleep(delay_seconds)

    return {
        "status": "completed",
        "results": results
    }
