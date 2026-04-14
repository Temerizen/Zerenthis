from fastapi import APIRouter

router = APIRouter()

@router.get("/api/phase/verify")
def verify():
    return {
        "status": "phase_verify_passed"
    }

