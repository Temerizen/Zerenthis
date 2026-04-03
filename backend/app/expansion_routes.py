from fastapi import APIRouter, Body
from .decision_engine import get_next
from .expansion_engine import build_expansion_pack, save_expansion_pack, get_expansion_history

router = APIRouter()

@router.post("/api/expansion/run")
def expansion_run(
    topic: str = Body("", embed=True)
):
    item = get_next()

    if topic and isinstance(item, dict) and item.get("message") == "No content available":
        item = {
            "topic": topic,
            "buyer": "",
            "promise": "",
            "content": "",
            "niche": "",
            "tone": ""
        }

    if not item or item.get("message") == "No content available":
        return {"message": "No content available for expansion"}

    pack = build_expansion_pack(item)
    save_expansion_pack(pack)
    return pack

@router.get("/api/expansion/history")
def expansion_history():
    return get_expansion_history()
