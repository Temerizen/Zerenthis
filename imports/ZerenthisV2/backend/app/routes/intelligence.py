from fastapi import APIRouter
from backend.app.engines.decision_engine import decide, get_current_topic
from backend.app.engines.target_engine import generate_targets

router = APIRouter()

@router.post("/intelligence/run")
def run_intelligence():
    return decide()

@router.get("/intelligence/targets")
def get_targets():
    return generate_targets()

@router.get("/intelligence/current")
def current():
    topic = get_current_topic()
    return {"current_topic": topic}
