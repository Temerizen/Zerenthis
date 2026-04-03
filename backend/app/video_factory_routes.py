from fastapi import APIRouter, Body
from backend.app.video_factory_engine import build_video_factory_package

router = APIRouter(prefix="/api/video-factory", tags=["video-factory"])

@router.post("")
def run_video_factory(data: dict = Body(...)):
    return build_video_factory_package(data)
