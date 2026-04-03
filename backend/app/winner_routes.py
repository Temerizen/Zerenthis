from fastapi import APIRouter
from .winners import load

router = APIRouter()

@router.get("/api/winners")
def winners():
    return load()
