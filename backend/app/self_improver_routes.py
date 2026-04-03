from fastapi import APIRouter, Body
from backend.app.self_improver_engine import generate_proposals, store_proposals, get_proposals, approve_proposal, execute_proposal
from backend.app.body_engine import recent_runs

router = APIRouter(tags=["self-improver"])

@router.post("/api/self-improver/run")
def run():
    history = recent_runs(10)
    props = generate_proposals(history)
    stored = store_proposals(props)
    return {"status":"ok","proposals":stored}

@router.get("/api/self-improver/proposals")
def list_props():
    return get_proposals()

@router.post("/api/self-improver/approve")
def approve(data: dict = Body(...)):
    return approve_proposal(data.get("id"))

@router.post("/api/self-improver/execute")
def execute(data: dict = Body(...)):
    return execute_proposal(data.get("id"))
