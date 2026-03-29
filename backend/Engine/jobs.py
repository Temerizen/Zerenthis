import threading, uuid

jobs = {}

def run_job(job_id, fn, *args):
    jobs[job_id]["status"] = "running"
    try:
        result = fn(*args)
        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = result
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)

def create_job(fn, *args):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued"}
    t = threading.Thread(target=run_job, args=(job_id, fn, *args))
    t.start()
    return job_id
