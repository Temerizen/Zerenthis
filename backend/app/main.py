from fastapi import FastAPI
from pydantic import BaseModel
import importlib

app = FastAPI()

class SystemRequest(BaseModel):
    engine: str
    payload: dict = {}

@app.get("/")
def root():
    return {"status": "Zerenthis running"}

@app.post("/api/system/run")
def run_system(req: SystemRequest):
    try:
        module_path = f"backend.app.engines.{req.engine}"
        module = importlib.import_module(module_path)

        if hasattr(module, "run"):
            result = module.run(req.payload)
            return {
                "engine": req.engine,
                "result": result
            }
        else:
            return {"error": "No run() function"}

    except Exception as e:
        return {"error": str(e)}
