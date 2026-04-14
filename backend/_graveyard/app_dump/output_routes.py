from fastapi import APIRouter
from .decision_engine import get_next
from .content_engine import build_script
from .video_engine import create_video
from .pdf_engine import create_pdf

router = APIRouter()

@router.post("/api/output/run")
def output_run():
    item = get_next()

    if not item or item.get("message"):
        return {"error": "No content available"}

    script = build_script(item)
    video = create_video(item["topic"], script)
    pdf = create_pdf(item["topic"], script)

    return {
        "script": script,
        "video": video,
        "pdf": pdf,
        "item": item
    }

