from __future__ import annotations

def run(payload: dict | None = None) -> dict:
    payload = payload or {}
    return {
        "status": "ok",
        "engine": "conversion_engine",
        "mode": "baseline",
        "message": "Builder generated baseline patch for conversion_engine.py",
        "input": payload
    }
