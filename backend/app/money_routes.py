from fastapi import APIRouter
from backend.app.core_engine import generate_store

router = APIRouter()

@router.post("/api/system/run-loop")
def run_loop():
    store = generate_store()
    return {
        "status": "loop completed",
        "products_ready": len(store)
    }
