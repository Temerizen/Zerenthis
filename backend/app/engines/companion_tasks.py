from __future__ import annotations
import json, os, time, uuid
from typing import Dict, Any, List

MEMORY_PATH = "backend/data/companion_memory.json"

def _default_memory():
    return {
        "user_profile": {},
        "active_tasks": [],
        "conversation_history": []
    }

def _load():
    if not os.path.exists(MEMORY_PATH):
        return _default_memory()
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return _default_memory()
    data.setdefault("user_profile", {})
    data.setdefault("active_tasks", [])
    data.setdefault("conversation_history", [])
    return data

def _save(data):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def create_task(title: str, priority: str = "normal", notes: str = ""):
    mem = _load()

    task = {
        "id": str(uuid.uuid4())[:8],
        "title": title.strip(),
        "status": "active",
        "priority": (priority or "normal").strip().lower(),
        "notes": notes.strip(),
        "created_at": time.time(),
        "updated_at": time.time(),
        "last_action": "task_created"
    }

    mem["active_tasks"].append(task)
    _save(mem)
    return {"status": "task_created", "task": task}

def list_tasks():
    mem = _load()
    return {
        "status": "ok",
        "count": len(mem["active_tasks"]),
        "tasks": mem["active_tasks"]
    }

def update_task(task_id: str, status: str = None, notes: str = None, last_action: str = None):
    mem = _load()

    for task in mem["active_tasks"]:
        if task.get("id") == task_id:
            if status:
                task["status"] = status.strip().lower()
            if notes is not None:
                task["notes"] = notes.strip()
            if last_action:
                task["last_action"] = last_action.strip()
            task["updated_at"] = time.time()
            _save(mem)
            return {"status": "task_updated", "task": task}

    return {"status": "not_found", "task_id": task_id}

def resume_task(task_id: str):
    mem = _load()

    for task in mem["active_tasks"]:
        if task.get("id") == task_id:
            task["status"] = "active"
            task["last_action"] = "task_resumed"
            task["updated_at"] = time.time()
            _save(mem)
            return {"status": "task_resumed", "task": task}

    return {"status": "not_found", "task_id": task_id}

def complete_task(task_id: str):
    mem = _load()

    for task in mem["active_tasks"]:
        if task.get("id") == task_id:
            task["status"] = "completed"
            task["last_action"] = "task_completed"
            task["updated_at"] = time.time()
            _save(mem)
            return {"status": "task_completed", "task": task}

    return {"status": "not_found", "task_id": task_id}
