from .queue import get_job

def process_job(job_id):
    job = get_job(job_id)
    if not job:
        return {"status": "not_found"}

    kind = job.get("kind")
    return {"status": "processed", "kind": kind}
