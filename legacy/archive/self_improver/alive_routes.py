from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter(prefix="/api/alive", tags=["alive"])

ROOT = Path(__file__).resolve().parents[2]

@router.get("/state")
def state():
    try:
        return json.loads((ROOT / "backend/data/self_improver/state.json").read_text())
    except:
        return {"status": "no state"}

@router.get("/memory")
def memory():
    try:
        return json.loads((ROOT / "backend/data/self_improver/memory.json").read_text())
    except:
        return {"status": "no memory"}

@router.get("/reflections")
def reflections():
    try:
        return json.loads((ROOT / "backend/data/self_improver/reflections.json").read_text())
    except:
        return {"status": "no reflections"}

