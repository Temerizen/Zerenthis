from __future__ import annotations

import json
from pathlib import Path
from fastapi import APIRouter

from backend.empire.engine import run_cycle, bootstrap

router = APIRouter(prefix="/api/empire", tags=["empire"])

ROOT = Path(__file__).resolve().parents[1]
EMPIRE_DIR = ROOT / "data" / "empire"

def _load(name: str, default):
    path = EMPIRE_DIR / name
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

@router.get("/state")
def empire_state():
    bootstrap()
    return _load("state.json", {})

@router.get("/memory")
def empire_memory():
    bootstrap()
    return _load("memory.json", {})

@router.get("/trends")
def empire_trends():
    bootstrap()
    return {"items": _load("trendboard.json", [])}

@router.get("/offers")
def empire_offers():
    bootstrap()
    return {"items": _load("offers.json", [])}

@router.get("/content-map")
def empire_content_map():
    bootstrap()
    return _load("content_map.json", {})

@router.get("/niches")
def empire_niches():
    bootstrap()
    return {"items": _load("niche_map.json", [])}

@router.get("/reflections")
def empire_reflections():
    bootstrap()
    return {"items": _load("reflections.json", [])[-30:]}

@router.post("/cycle")
def empire_cycle():
    bootstrap()
    return run_cycle()
