from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
JOBS_DIR = ROOT / "data" / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)

def _job_file(job_id: str) -> Path:
    return JOBS_DIR / f"{job_id}.json"

def _save_job(job_id: str, data: dict[str, Any]) -> None:
    _job_file(job_id).write_text(json.dumps(data, indent=2), encoding="utf-8")

def _load_job(job_id: str) -> dict[str, Any]:
    path = _job_file(job_id)
    if not path.exists():
        return {"status": "not_found"}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def get_job(job_id: str) -> dict[str, Any]:
    return _load_job(job_id)

def create_job(kind: str, payload: dict[str, Any], fn: Callable[..., Any], **kwargs) -> str:
    job_id = str(uuid.uuid4())
    _save_job(job_id, {
        "job_id": job_id,
        "kind": kind,
        "status": "queued",
        "payload": payload,
        "created_ts": time.time(),
    })

    def _runner():
        _save_job(job_id, {
            "job_id": job_id,
            "kind": kind,
            "status": "running",
            "payload": payload,
            "created_ts": time.time(),
        })
        try:
            result = fn(**kwargs)
            _save_job(job_id, {
                "job_id": job_id,
                "kind": kind,
                "status": "completed",
                "payload": payload,
                "result": result,
                "completed_ts": time.time(),
            })
        except Exception as e:
            _save_job(job_id, {
                "job_id": job_id,
                "kind": kind,
                "status": "failed",
                "payload": payload,
                "error": str(e),
                "failed_ts": time.time(),
            })

    threading.Thread(target=_runner, daemon=True).start()
    return job_id
