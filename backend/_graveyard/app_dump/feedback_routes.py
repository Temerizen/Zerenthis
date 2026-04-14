from fastapi import APIRouter, Body
from backend.app.feedback_engine import track_view, track_click, track_sale

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@router.post("/view")
def view(data: dict = Body(...)):
    return track_view(data)

@router.post("/click")
def click(data: dict = Body(...)):
    return track_click(data)

@router.post("/sale")
def sale(data: dict = Body(...)):
    return track_sale(data)


