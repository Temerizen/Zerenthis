import uuid
import datetime

_QUEUE = []

def enqueue(task_type: str, payload: dict):
    item = {
        "queue_id": uuid.uuid4().hex,
        "task_type": task_type,
        "payload": payload,
        "status": "queued",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    _QUEUE.append(item)
    return item

def list_queue():
    return list(reversed(_QUEUE[-200:]))

def clear_queue():
    _QUEUE.clear()
    return True

