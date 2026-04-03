from fastapi import APIRouter, Body
from backend.app.video_engine import create_video_package

router = APIRouter(prefix="/api/video", tags=["video"])

@router.post("/generate")
def generate(data: dict = Body(...)):
    return create_video_package(data)

