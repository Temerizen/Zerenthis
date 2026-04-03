from fastapi import APIRouter, Request, HTTPException
import os

router = APIRouter()

def is_founder(request: Request):
    key = os.getenv("FOUNDER_KEY", "")
    return request.headers.get("x-founder-key") == key

@router.get("/api/founder/ping")
def founder_ping(request: Request):
    if not is_founder(request):
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"status": "founder access confirmed"}

@router.post("/api/founder/toggle-autopilot")
def toggle_autopilot(request: Request):
    if not is_founder(request):
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"autopilot": "toggled (placeholder)"}
