from fastapi import APIRouter
from backend.self_improver.engine import *

router = APIRouter(prefix="/self", tags=["Self Improver"])

@router.post("/propose")
def propose_route(data: dict):
    return propose(data["title"], data["reason"], data["steps"])

@router.get("/pending")
def pending_route():
    return pending()

@router.post("/approve/{pid}")
def approve_route(pid: str):
    approve(pid)
    return {"ok": True}

@router.post("/reject/{pid}")
def reject_route(pid: str):
    reject(pid)
    return {"ok": True}

@router.post("/execute/{pid}")
def execute_route(pid: str):
    return execute(pid)

