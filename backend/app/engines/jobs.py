from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Callable, Dict

JOBS: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()


def create_job(kind: str, payload: dict, worker: Callable[..., dict], *args, **kwargs) -> str:
    job_id = str(uuid.uuid4())
    with _LOCK:
        JOBS[job_id] = {
            "job_id": job_id,
            "kind": kind,
            "status": "queued",
            "created_at": time.time(),
            "payload": payload,
        }

    thread = threading.Thread(
        target=_run_job,
        args=(job_id, worker, args, kwargs),
        daemon=True,
    )
    thread.start()
    return job_id


def _run_job(job_id: str, worker: Callable[..., dict], args: tuple, kwargs: dict) -> None:
    with _LOCK:
        JOBS[job_id]["status"] = "running"
        JOBS[job_id]["started_at"] = time.time()

    try:
        result = worker(*args, **kwargs)
        with _LOCK:
            JOBS[job_id]["status"] = "done"
            JOBS[job_id]["finished_at"] = time.time()
            JOBS[job_id].update(result)
    except Exception as exc:
        with _LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["finished_at"] = time.time()
            JOBS[job_id]["error"] = str(exc)


def get_job(job_id: str) -> dict:
    return JOBS.get(job_id, {"job_id": job_id, "status": "not_found"})


def list_jobs(limit: int = 100) -> list[dict]:
    items = list(JOBS.values())
    items.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return items[:limit]

