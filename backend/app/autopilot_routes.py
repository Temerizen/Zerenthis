from fastapi import APIRouter, Body
from .packs_store import add_pack
from .decision_engine import build_queue, get_next

router = APIRouter()

@router.post("/api/packs/add")
def add_manual_pack(
    topic: str = Body(..., embed=True),
    buyer: str = Body("", embed=True),
    promise: str = Body("", embed=True),
    content: str = Body("", embed=True),
    file_name: str = Body("", embed=True),
    niche: str = Body("", embed=True),
    tone: str = Body("", embed=True),
    bonus: str = Body("", embed=True),
    notes: str = Body("", embed=True)
):
    pack = add_pack(
        topic=topic,
        buyer=buyer,
        promise=promise,
        content=content,
        file_name=file_name,
        niche=niche,
        tone=tone,
        bonus=bonus,
        notes=notes,
    )
    return {"saved": True, "pack": pack}

@router.post("/api/autopilot/run")
def autopilot_run(
    topic: str = Body(..., embed=True),
    buyer: str = Body("New creators", embed=True),
    promise: str = Body("start posting quickly", embed=True),
    content: str = Body("", embed=True),
    niche: str = Body("Content Monetization", embed=True),
    tone: str = Body("Premium", embed=True),
    bonus: str = Body("", embed=True),
    notes: str = Body("", embed=True)
):
    add_pack(
        topic=topic,
        buyer=buyer,
        promise=promise,
        content=content,
        niche=niche,
        tone=tone,
        bonus=bonus,
        notes=notes,
    )
    queue = build_queue()
    next_item = get_next()
    return {
        "status": "autopilot cycle complete",
        "queue_count": len(queue),
        "next": next_item
    }
