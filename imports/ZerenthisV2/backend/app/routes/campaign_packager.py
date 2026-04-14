from fastapi import APIRouter
from backend.app.engines.campaign_packager import run

router = APIRouter()

@router.post("/api/campaign/build")
def build_campaign():
    return run()
