from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.builder.safe_builder import apply_safe_change

router = APIRouter()

class ChangeRequest(BaseModel):
    file_path: str
    new_code: str

@router.post("/api/builder/apply")
def apply_change(req: ChangeRequest):
    return apply_safe_change(req.file_path, req.new_code)
