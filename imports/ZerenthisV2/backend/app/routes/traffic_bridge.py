from fastapi import APIRouter
from backend.app.engines.traffic_bridge import run

router = APIRouter()

@router.post("/api/traffic/bridge")
def bridge():
    return run()
