from fastapi import APIRouter
from backend.app.expansion import run_expansion
from backend.app.self_improver import propose_change, approve_proposal

router = APIRouter()

@router.post("/api/system/expand")
def expand():
    return run_expansion()

@router.post("/api/system/propose")
def propose():
    return propose_change()

@router.post("/api/system/approve/{pid}")
def approve(pid: int):
    return approve_proposal(pid)
