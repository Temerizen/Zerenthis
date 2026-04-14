from fastapi import APIRouter
from backend.app.cognition.conflict_engine import resolve_conflicts

router = APIRouter()

@router.post("/api/conflict/resolve")
def resolve():
    return resolve_conflicts()
