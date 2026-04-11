
from fastapi import APIRouter
from backend.app.engines.intelligence_core import observe_system, build_intelligent_topic, simulate_outcome

router = APIRouter()

@router.post("/observe")
def observe(data: dict):
    return observe_system(data)

@router.post("/build")
def build():
    return build_intelligent_topic()

@router.post("/simulate")
def simulate(data: dict):
    return simulate_outcome(data.get("topic", ""))

