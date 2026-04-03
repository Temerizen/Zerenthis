from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

SYSTEM_STATE = {
    "mode": "idle",
    "last_command": None,
    "last_updated": None
}

@router.get("/status")
def status():
    return {
        "system": "Zerenthis Commander",
        "state": SYSTEM_STATE
    }

@router.post("/command")
def run_command(cmd: str):
    SYSTEM_STATE["mode"] = "processing"
    SYSTEM_STATE["last_command"] = cmd
    SYSTEM_STATE["last_updated"] = str(datetime.utcnow())

    # Placeholder for future intelligence logic
    return {
        "message": f"Command '{cmd}' received",
        "status": "queued"
    }