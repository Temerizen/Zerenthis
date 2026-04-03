from fastapi import APIRouter
from app.self_surgeon import run_surgeon, create_proposals

router = APIRouter(prefix="/api/surgeon", tags=["surgeon"])

@router.post("/run")
def run():
    return run_surgeon()

@router.get("/proposals")
def proposals():
    return create_proposals()
