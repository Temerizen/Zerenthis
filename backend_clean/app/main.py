from fastapi import FastAPI, APIRouter
from datetime import datetime

app = FastAPI()

# ========================
# GLOBAL SYSTEM STATE
# ========================

SYSTEM_STATE = {
    "mode": "idle",
    "last_command": None,
    "last_updated": None,
    "tasks": [],
    "logs": []
}

# ========================
# BASIC ROUTES
# ========================

@app.get("/")
def root():
    return {
        "status": "Zerenthis Core Online",
        "mode": SYSTEM_STATE["mode"]
    }

@app.get("/health")
def health():
    return {"ok": True}

# ========================
# COMMANDER SYSTEM
# ========================

commander = APIRouter()

@commander.get("/status")
def status():
    return {
        "system": "Zerenthis Commander",
        "state": SYSTEM_STATE
    }

@commander.get("/command")
def run_command(cmd: str):
    SYSTEM_STATE["mode"] = "processing"
    SYSTEM_STATE["last_command"] = cmd
    SYSTEM_STATE["last_updated"] = str(datetime.utcnow())

    # Add task to queue
    task = {
        "id": len(SYSTEM_STATE["tasks"]) + 1,
        "command": cmd,
        "status": "queued",
        "created_at": str(datetime.utcnow())
    }

    SYSTEM_STATE["tasks"].append(task)

    SYSTEM_STATE["logs"].append(f"Command received: {cmd}")

    return {
        "message": f"Command '{cmd}' received",
        "task": task
    }

# ========================
# TASK SYSTEM
# ========================

tasks_router = APIRouter()

@tasks_router.get("/list")
def list_tasks():
    return {"tasks": SYSTEM_STATE["tasks"]}

@tasks_router.get("/run")
def run_next_task():
    if not SYSTEM_STATE["tasks"]:
        return {"message": "No tasks in queue"}

    task = SYSTEM_STATE["tasks"][0]
    task["status"] = "running"

    SYSTEM_STATE["logs"].append(f"Running task: {task['command']}")

    # VERY BASIC EXECUTION LOGIC (placeholder)
    result = f"Executed: {task['command']}"

    task["status"] = "completed"
    task["result"] = result
    task["finished_at"] = str(datetime.utcnow())

    SYSTEM_STATE["logs"].append(result)

    # remove from queue
    SYSTEM_STATE["tasks"].pop(0)

    SYSTEM_STATE["mode"] = "idle"

    return {
        "message": "Task executed",
        "result": result
    }

# ========================
# LOG SYSTEM
# ========================

logs_router = APIRouter()

@logs_router.get("/")
def get_logs():
    return {"logs": SYSTEM_STATE["logs"]}

# ========================
# FUTURE MODULE PLACEHOLDERS
# ========================

@app.get("/system/info")
def system_info():
    return {
        "name": "Zerenthis",
        "version": "0.1",
        "modules": [
            "commander",
            "tasks",
            "logs",
            "future: self_improver",
            "future: product_engine",
            "future: video_engine"
        ]
    }

# ========================
# REGISTER ROUTERS
# ========================

app.include_router(commander, prefix="/commander")
app.include_router(tasks_router, prefix="/tasks")
app.include_router(logs_router, prefix="/logs")