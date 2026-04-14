from fastapi import APIRouter
from backend.app.engines.reality_exporter import run

router = APIRouter()

@router.post("/api/reality/export")
def export_real_package():
    return run()
