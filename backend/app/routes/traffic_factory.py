from fastapi import APIRouter
from backend.app.engines.traffic_factory import run

router = APIRouter()

@router.post("/api/traffic/generate")
def generate_traffic():
    return run()

