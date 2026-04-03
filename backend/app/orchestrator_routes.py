from fastapi import APIRouter, Body
from .packs_store import add_pack
from .decision_engine import build_queue, get_next
from .expansion_engine import build_expansion_pack, save_expansion_pack

router = APIRouter()

@router.post("/api/orchestrator/run")
def orchestrator_run(
    topic: str = Body(..., embed=True),
    buyer: str = Body("New creators", embed=True),
    promise: str = Body("start posting quickly", embed=True),
    content: str = Body("", embed=True),
    niche: str = Body("Content Monetization", embed=True),
    tone: str = Body("Premium", embed=True),
    bonus: str = Body("", embed=True),
    notes: str = Body("", embed=True)
):
    saved = add_pack(
        topic=topic,
        buyer=buyer,
        promise=promise,
        content=content,
        niche=niche,
        tone=tone,
        bonus=bonus,
        notes=notes
    )

    queue = build_queue()
    next_item = get_next()

    if not next_item or next_item.get("message") == "No content available":
        return {
            "status": "orchestrator complete",
            "saved": saved,
            "queue_count": len(queue),
            "next": {"message": "No content available"},
            "expansion": None
        }

    expansion = build_expansion_pack(next_item)
    save_expansion_pack(expansion)

    return {
        "status": "orchestrator complete",
        "saved": saved,
        "queue_count": len(queue),
        "next": next_item,
        "expansion": expansion
    }
