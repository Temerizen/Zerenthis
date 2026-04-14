jobs = []

def add_job(job):
    jobs.append(job)

def get_job(job_id):
    for job in jobs:
        if job.get("id") == job_id:
            return job
    return None
