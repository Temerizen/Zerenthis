from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.engines.autopilot_engine import run

router = APIRouter()

class AutoInput(BaseModel):
    goal: str

@router.post("/autopilot")
def autopilot(input: AutoInput):
    return run({"goal": input.goal})