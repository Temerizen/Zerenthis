from fastapi import APIRouter
from backend.app.engines.real_traffic_bridge import run

router = APIRouter()

@router.post("/api/traffic/real")
def get_real_traffic():
    return run()
