from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/api/dashboard")
def dashboard():
    files = os.listdir("backend/outputs") if os.path.exists("backend/outputs") else []
    return {
        "status": "online",
        "mode": "autonomous",
        "outputs": files[-10:]
    }

