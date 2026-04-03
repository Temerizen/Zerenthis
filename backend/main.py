from fastapi import FastAPI, BackgroundTasks
import uuid, time

app = FastAPI()

jobs = {}

def run_job(job_id, prompt):
    time.sleep(2)

    result = {
        "title": prompt,
        "files": {
            "product": f"{prompt}_guide.txt",
            "script": f"{prompt}_script.txt",
            "video": f"{prompt}_video.mp4"
        }
    }

    jobs[job_id]["status"] = "done"
    jobs[job_id]["result"] = result

@app.post("/api/generate")
def generate(data: dict, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing"}

    bg.add_task(run_job, job_id, data.get("prompt"))

    return {"job_id": job_id}

@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    return jobs.get(job_id, {"error": "not found"})
