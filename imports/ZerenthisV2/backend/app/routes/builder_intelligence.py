from fastapi import APIRouter
from pydantic import BaseModel
import os

from backend.app.builder.safe_builder import apply_safe_change
from backend.app.builder.builder_intelligence import analyze_change

router = APIRouter()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))


class SmartChangeRequest(BaseModel):
    file_path: str
    new_code: str


def resolve_path(file_path: str) -> str:
    if os.path.isabs(file_path):
        return file_path
    return os.path.abspath(os.path.join(BASE_DIR, file_path))


@router.post("/api/builder/smart-apply")
def smart_apply(req: SmartChangeRequest):
    real_path = resolve_path(req.file_path)

    if not os.path.exists(real_path):
        return {"status": "error", "reason": "file_not_found"}

    # 🔥 CRITICAL: read BEFORE anything else
    with open(real_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    # 🔥 analyze against TRUE original
    analysis = analyze_change(real_path, original_code, req.new_code)

    if analysis["status"] != "approved":
        return {
            "status": "rejected",
            "analysis": analysis
        }

    # 🔥 apply ONLY after analysis passes
    result = apply_safe_change(real_path, req.new_code)

    return {
        "status": result["status"],
        "analysis": analysis,
        "backup": result.get("backup")
    }
