import json
import uuid

TASK_FILE = "backend/data/tasks.json"

def load_tasks():
    with open(TASK_FILE) as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def create_task(plan):
    tasks = load_tasks()
    task = {
        "id": str(uuid.uuid4()),
        "plan": plan,
        "status": "pending"
    }
    tasks.append(task)
    save_tasks(tasks)
    return task

