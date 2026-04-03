from fastapi import FastAPI, APIRouter
from datetime import datetime
import os

app = FastAPI()

# ========================
# GLOBAL SYSTEM STATE
# ========================

SYSTEM_STATE = {
    "mode": "idle",
    "last_command": None,
    "last_updated": None,
    "tasks": [],
    "logs": [],
    "memory": {},
    "stats": {
        "commands_run": 0,
        "tasks_completed": 0
    }
}

# ========================
# UTILITIES
# ========================

def log(msg):
    SYSTEM_STATE["logs"].append(f"[{datetime.utcnow()}] {msg}")

def add_task(cmd):
    task = {
        "id": len(SYSTEM_STATE["tasks"]) + 1,
        "command": cmd,
        "status": "queued",
        "created_at": str(datetime.utcnow())
    }
    SYSTEM_STATE["tasks"].append(task)
    return task

# ========================
# BASIC ROUTES
# ========================

@app.get("/")
def root():
    return {
        "status": "Zerenthis MAX Core Online",
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
        "system": "Zerenthis MAX Commander",
        "state": SYSTEM_STATE
    }

@commander.get("/command")
def run_command(cmd: str):
    SYSTEM_STATE["mode"] = "processing"
    SYSTEM_STATE["last_command"] = cmd
    SYSTEM_STATE["last_updated"] = str(datetime.utcnow())
    SYSTEM_STATE["stats"]["commands_run"] += 1

    task = add_task(cmd)
    log(f"Command received: {cmd}")

    return {
        "message": f"Command '{cmd}' queued",
        "task": task
    }

# ========================
# TASK ENGINE
# ========================

tasks = APIRouter()

def execute_logic(command):
    # EXTEND THIS SAFELY LATER
    if "scan" in command:
        return "Repo scan placeholder complete"

    if "build" in command:
        return "Build sequence placeholder complete"

    if "status" in command:
        return f"System running in {SYSTEM_STATE['mode']} mode"

    return f"Executed generic command: {command}"

@tasks.get("/run")
def run_next():
    if not SYSTEM_STATE["tasks"]:
        return {"message": "No tasks"}

    task = SYSTEM_STATE["tasks"][0]
    task["status"] = "running"
    log(f"Running task: {task['command']}")

    result = execute_logic(task["command"])

    task["status"] = "completed"
    task["result"] = result
    task["finished_at"] = str(datetime.utcnow())

    SYSTEM_STATE["stats"]["tasks_completed"] += 1

    log(result)

    SYSTEM_STATE["tasks"].pop(0)
    SYSTEM_STATE["mode"] = "idle"

    return {
        "message": "Task complete",
        "result": result
    }

@tasks.get("/list")
def list_tasks():
    return {"tasks": SYSTEM_STATE["tasks"]}

# ========================
# MEMORY SYSTEM
# ========================

memory = APIRouter()

@memory.get("/set")
def set_memory(key: str, value: str):
    SYSTEM_STATE["memory"][key] = value
    log(f"Memory set: {key}")
    return {"message": "stored", "memory": SYSTEM_STATE["memory"]}

@memory.get("/get")
def get_memory(key: str):
    return {"value": SYSTEM_STATE["memory"].get(key)}

# ========================
# LOG SYSTEM
# ========================

logs = APIRouter()

@logs.get("/")
def get_logs():
    return {"logs": SYSTEM_STATE["logs"][-50:]}

# ========================
# SELF-IMPROVER (SAFE MODE)
# ========================

self_improver = APIRouter()

@self_improver.get("/suggest")
def suggest():
    # This is where future intelligence connects
    suggestion = {
        "proposal": "Stabilize backend imports",
        "risk": "low",
        "action": "refactor import paths"
    }
    log("Self-improver generated suggestion")
    return suggestion

@self_improver.get("/apply")
def apply_change(action: str):
    # SAFE placeholder only
    log(f"Apply requested: {action}")
    return {
        "status": "pending_approval",
        "message": "Action requires approval"
    }

# ========================
# SYSTEM INFO
# ========================

@app.get("/system/info")
def info():
    return {
        "name": "Zerenthis MAX",
        "modules": [
            "commander",
            "tasks",
            "memory",
            "logs",
            "self_improver"
        ],
        "stats": SYSTEM_STATE["stats"]
    }

# ========================
# ROUTERS
# ========================

app.include_router(commander, prefix="/commander")
app.include_router(tasks, prefix="/tasks")
app.include_router(memory, prefix="/memory")
app.include_router(logs, prefix="/logs")
app.include_router(self_improver, prefix="/self")