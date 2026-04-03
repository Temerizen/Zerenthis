from fastapi import FastAPI, APIRouter
from datetime import datetime

app = FastAPI()

# ========================
# BASIC HEALTH ROUTES
# ========================

@app.get("/")
def root():
    return {"status": "Zerenthis staging backend live"}

@app.get("/health")
def health():
    return {"ok": True}

# ========================
# COMMANDER SYSTEM
# ========================

commander_router = APIRouter()

SYSTEM_STATE = {
    "mode": "idle",
    "last_command": None,
    "last_updated": None
}

@commander_router.get("/status")
def status():
    return {
        "system": "Zerenthis Commander",
        "state": SYSTEM_STATE
    }

@commander_router.post("/command")
def run_command(cmd: str):
    SYSTEM_STATE["mode"] = "processing"
    SYSTEM_STATE["last_command"] = cmd
    SYSTEM_STATE["last_updated"] = str(datetime.utcnow())

    return {
        "message": f"Command '{cmd}' received",
        "status": "queued"
    }

app.include_router(commander_router, prefix="/commander")