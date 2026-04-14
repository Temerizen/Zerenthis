from fastapi import APIRouter, Body
from pathlib import Path
from datetime import datetime, timezone
import json, uuid

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
TASK_DIR = DATA_DIR / "tasks"
QUEUE_FILE = TASK_DIR / "queue.json"
PROJECTS_FILE = TASK_DIR / "projects.json"

TASK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _now():
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "task")).strip("_")[:80] or "task"

def load_queue():
    data = _read_json(QUEUE_FILE, {"tasks": []})
    if not isinstance(data, dict):
        data = {"tasks": []}
    data.setdefault("tasks", [])
    return data

def save_queue(data: dict):
    _write_json(QUEUE_FILE, data)

def load_projects():
    data = _read_json(PROJECTS_FILE, {"projects": []})
    if not isinstance(data, dict):
        data = {"projects": []}
    data.setdefault("projects", [])
    return data

def save_projects(data: dict):
    _write_json(PROJECTS_FILE, data)

def add_task(title: str, kind: str, payload: dict, priority: int = 5, project_id: str = ""):
    queue = load_queue()
    task = {
        "id": f"task_{uuid.uuid4().hex[:10]}",
        "title": title or "Untitled Task",
        "kind": kind or "general",
        "payload": payload or {},
        "priority": int(priority),
        "project_id": project_id or "",
        "status": "queued",
        "created_at": _now(),
        "updated_at": _now(),
        "attempts": 0,
        "result": None,
        "error": ""
    }
    queue["tasks"].append(task)
    queue["tasks"] = sorted(queue["tasks"], key=lambda x: (-int(x.get("priority", 5)), x.get("created_at", "")))[-500:]
    save_queue(queue)
    return task

def get_task(task_id: str):
    queue = load_queue()
    for t in queue.get("tasks", []):
        if t.get("id") == task_id:
            return t
    return None

def update_task(task_id: str, **fields):
    queue = load_queue()
    for i, t in enumerate(queue.get("tasks", [])):
        if t.get("id") == task_id:
            t.update(fields)
            t["updated_at"] = _now()
            queue["tasks"][i] = t
            save_queue(queue)
            return t
    return None

def create_project(name: str, objective: str, metadata: dict | None = None):
    data = load_projects()
    project = {
        "id": f"proj_{uuid.uuid4().hex[:10]}",
        "name": name or "Untitled Project",
        "objective": objective or "",
        "metadata": metadata or {},
        "status": "active",
        "created_at": _now(),
        "updated_at": _now(),
        "task_ids": [],
        "memory": {
            "notes": [],
            "winners": [],
            "risks": [],
            "artifacts": []
        }
    }
    data["projects"].append(project)
    data["projects"] = data["projects"][-200:]
    save_projects(data)
    return project

def attach_task_to_project(project_id: str, task_id: str):
    data = load_projects()
    for i, p in enumerate(data.get("projects", [])):
        if p.get("id") == project_id:
            if task_id not in p["task_ids"]:
                p["task_ids"].append(task_id)
            p["updated_at"] = _now()
            data["projects"][i] = p
            save_projects(data)
            return p
    return None

def append_project_memory(project_id: str, bucket: str, item):
    data = load_projects()
    for i, p in enumerate(data.get("projects", [])):
        if p.get("id") == project_id:
            p.setdefault("memory", {})
            p["memory"].setdefault(bucket, [])
            p["memory"][bucket].append(item)
            p["memory"][bucket] = p["memory"][bucket][-200:]
            p["updated_at"] = _now()
            data["projects"][i] = p
            save_projects(data)
            return p
    return None

def next_task():
    queue = load_queue()
    queued = [t for t in queue.get("tasks", []) if t.get("status") == "queued"]
    queued = sorted(queued, key=lambda x: (-int(x.get("priority", 5)), x.get("created_at", "")))
    return queued[0] if queued else None

def _write_output(name: str, data: dict):
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

def _execute_task(task: dict):
    kind = (task.get("kind") or "").lower()
    payload = task.get("payload") or {}
    title = task.get("title", "task")

    if kind in ("generate", "content", "money", "offer"):
        try:
            from backend.app.money_sweep import founder_full_stack_generate
            result = founder_full_stack_generate({
                "topic": payload.get("topic", title),
                "buyer": payload.get("buyer", "Creators"),
                "promise": payload.get("promise", "move faster"),
                "niche": payload.get("niche", "Content Monetization"),
                "tone": payload.get("tone", "Premium"),
                "bonus": payload.get("bonus", "durable task hooks"),
                "notes": payload.get("notes", "durable inbox task execution")
            })
            return {"status": "ok", "result": result}
        except Exception as e:
            return {"status": "fallback", "error": str(e), "result": {"title": title, "payload": payload}}

    if kind in ("monetize", "sales"):
        try:
            from backend.app.monetization import monetize_package
            result = monetize_package({
                "topic": payload.get("topic", title),
                "buyer": payload.get("buyer", "Creators"),
                "promise": payload.get("promise", "make money faster"),
                "niche": payload.get("niche", "Content Monetization"),
                "tone": payload.get("tone", "Premium"),
                "bonus": payload.get("bonus", "durable monetization stack"),
                "notes": payload.get("notes", "durable inbox monetize execution")
            })
            return {"status": "ok", "result": result}
        except Exception as e:
            return {"status": "fallback", "error": str(e), "result": {"title": title, "payload": payload}}

    if kind in ("winner", "evolve"):
        try:
            from backend.app.winner_cycle import run_winner_cycle
            result = run_winner_cycle({
                "topic": payload.get("topic", title),
                "buyer": payload.get("buyer", "Creators"),
                "promise": payload.get("promise", "grow faster"),
                "niche": payload.get("niche", "Content Monetization"),
                "notes": payload.get("notes", "durable inbox winner execution")
            })
            return {"status": "ok", "result": result}
        except Exception as e:
            return {"status": "fallback", "error": str(e), "result": {"title": title, "payload": payload}}

    return {
        "status": "ok",
        "result": {
            "message": "task executed in generic mode",
            "title": title,
            "payload": payload
        }
    }

@router.post("/api/inbox/project/create")
def inbox_project_create(payload: dict = Body(...)):
    project = create_project(
        name=payload.get("name", "Untitled Project"),
        objective=payload.get("objective", ""),
        metadata=payload.get("metadata", {})
    )
    return {
        "status": "ok",
        "phase": "durable inbox + long-horizon tasks",
        "project": project
    }

@router.post("/api/inbox/task/add")
def inbox_task_add(payload: dict = Body(...)):
    task = add_task(
        title=payload.get("title", "Untitled Task"),
        kind=payload.get("kind", "general"),
        payload=payload.get("payload", {}),
        priority=int(payload.get("priority", 5)),
        project_id=payload.get("project_id", "")
    )
    if task.get("project_id"):
        attach_task_to_project(task["project_id"], task["id"])
    return {
        "status": "ok",
        "phase": "durable inbox + long-horizon tasks",
        "task": task
    }

@router.post("/api/inbox/task/run-next")
def inbox_run_next():
    task = next_task()
    if not task:
        return {
            "status": "ok",
            "phase": "durable inbox + long-horizon tasks",
            "message": "no queued tasks"
        }

    update_task(task["id"], status="running", attempts=int(task.get("attempts", 0)) + 1)
    outcome = _execute_task(task)

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    artifact_url = _write_output(f"{_slug(task.get('title','task'))}_task_{stamp}.json", {
        "time": _now(),
        "task": task,
        "outcome": outcome
    })

    final_status = "completed" if outcome.get("status") in ("ok", "fallback") else "failed"
    updated = update_task(
        task["id"],
        status=final_status,
        result={**outcome, "artifact_url": artifact_url},
        error=outcome.get("error", "")
    )

    if task.get("project_id"):
        append_project_memory(task["project_id"], "artifacts", {
            "time": _now(),
            "task_id": task["id"],
            "title": task.get("title", ""),
            "artifact_url": artifact_url,
            "status": final_status
        })
        if final_status == "completed":
            append_project_memory(task["project_id"], "notes", {
                "time": _now(),
                "text": f"Completed task: {task.get('title','')}"
            })

    return {
        "status": "ok",
        "phase": "durable inbox + long-horizon tasks",
        "task": updated,
        "artifact_url": artifact_url
    }

@router.get("/api/inbox/status")
def inbox_status():
    queue = load_queue()
    projects = load_projects()

    tasks = queue.get("tasks", [])
    queued = [t for t in tasks if t.get("status") == "queued"]
    running = [t for t in tasks if t.get("status") == "running"]
    completed = [t for t in tasks if t.get("status") == "completed"]
    failed = [t for t in tasks if t.get("status") == "failed"]

    return {
        "status": "ok",
        "phase": "durable inbox + long-horizon tasks",
        "counts": {
            "queued": len(queued),
            "running": len(running),
            "completed": len(completed),
            "failed": len(failed),
            "projects": len(projects.get("projects", []))
        },
        "next_task": next_task(),
        "recent_tasks": sorted(tasks, key=lambda x: x.get("updated_at", ""), reverse=True)[:12],
        "recent_projects": sorted(projects.get("projects", []), key=lambda x: x.get("updated_at", ""), reverse=True)[:12]
    }

@router.get("/api/inbox/project/{project_id}")
def inbox_project_get(project_id: str):
    projects = load_projects()
    project = next((p for p in projects.get("projects", []) if p.get("id") == project_id), None)
    if not project:
        return {"status": "error", "error": "project not found"}

    queue = load_queue()
    task_lookup = {t.get("id"): t for t in queue.get("tasks", [])}
    project_tasks = [task_lookup[tid] for tid in project.get("task_ids", []) if tid in task_lookup]

    return {
        "status": "ok",
        "phase": "durable inbox + long-horizon tasks",
        "project": project,
        "tasks": project_tasks
    }

@router.post("/api/inbox/project/note")
def inbox_project_note(payload: dict = Body(...)):
    project_id = payload.get("project_id", "")
    note = payload.get("note", "")
    bucket = payload.get("bucket", "notes")
    project = append_project_memory(project_id, bucket, {
        "time": _now(),
        "text": note
    })
    if not project:
        return {"status": "error", "error": "project not found"}
    return {
        "status": "ok",
        "phase": "durable inbox + long-horizon tasks",
        "project": project
    }

