from backend.app.execution.routes import router as execution_router
from backend.app.hybrid.routes import router as hybrid_router
from fastapi import FastAPI
from pydantic import BaseModel
import importlib

app = FastAPI()
app.include_router(execution_router)
app.include_router(hybrid_router)
from backend.app.routes.live_feed import router as live_router
app.include_router(live_router)

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





