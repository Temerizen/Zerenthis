from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from backend.app.engines.engine_loader import run_engine

router = APIRouter()

class RunRequest(BaseModel):
    engine: str
    payload: Dict[str, Any]

@router.get("/health")
def health():
    return {"ok": True, "route": "system"}

@router.post("/run")
def run(req: RunRequest):
    result = run_engine(req.engine, req.payload)
    return {"result": result}