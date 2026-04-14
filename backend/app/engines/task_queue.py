import json, os, time, copy

QUEUE_PATH = "backend/data/task_queue.json"
LOG_PATH = "backend/data/task_log.json"

def load_json(path, default=None):
    default = [] if default is None else default
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def enqueue_task(task):
    queue = load_json(QUEUE_PATH, [])
    task = dict(task)
    task["id"] = int(time.time() * 1000)
    task["status"] = "pending"
    task["created_at"] = time.time()
    queue.append(task)
    save_json(QUEUE_PATH, queue)
    return task

def get_next_task():
    queue = load_json(QUEUE_PATH, [])
    for task in queue:
        if task.get("status") == "pending":
            task["status"] = "processing"
            task["started_at"] = time.time()
            save_json(QUEUE_PATH, queue)
            return task
    return None

def complete_task(task, result):
    queue = load_json(QUEUE_PATH, [])
    log = load_json(LOG_PATH, [])

    completed_task = None
    for t in queue:
        if t["id"] == task["id"]:
            t["status"] = "done"
            t["completed_at"] = time.time()
            t["result"] = result
            completed_task = copy.deepcopy(t)
            break

    if completed_task is None:
        completed_task = copy.deepcopy(task)
        completed_task["status"] = "done"
        completed_task["completed_at"] = time.time()
        completed_task["result"] = result

    log.append({
        "task": completed_task,
        "result": result,
        "timestamp": time.time()
    })

    save_json(QUEUE_PATH, queue)
    save_json(LOG_PATH, log[-50:])

def process_next_task():
    task = get_next_task()
    if not task:
        return {"processed": False, "reason": "no_tasks"}

    result = {
        "status": "executed",
        "type": task.get("type"),
        "target": task.get("target")
    }

    complete_task(task, result)
    return {
        "processed": True,
        "task": task,
        "result": result
    }
