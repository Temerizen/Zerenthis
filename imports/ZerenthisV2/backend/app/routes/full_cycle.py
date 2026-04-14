from pathlib import Path
import json
from datetime import datetime
from fastapi import APIRouter
from backend.app.engines.intelligence_priority_engine import run_priority_engine
from backend.app.engines.product_engine import run_product_engine

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "backend" / "data"
CURRENT_TOPIC_FILE = DATA_DIR / "current_topic.json"
MANIFEST_FILE = DATA_DIR / "last_full_cycle.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/api/intelligence/full-cycle")
def full_cycle():
    priority = run_priority_engine()
    top = priority.get("top_target") or {}

    if top.get("topic"):
        CURRENT_TOPIC_FILE.write_text(
            json.dumps(
                {
                    "topic": top.get("topic"),
                    "source": top.get("source"),
                    "revenue": top.get("revenue", 0),
                    "conversions": top.get("conversions", 0),
                    "total_score": top.get("total_score", 0),
                    "locked_at": datetime.utcnow().isoformat()
                },
                indent=2
            ),
            encoding="utf-8"
        )

    product = run_product_engine()

    payload = {
        "status": "full_cycle_complete",
        "priority": priority,
        "product": product
    }

    MANIFEST_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

@router.get("/api/intelligence/last-cycle")
def last_cycle():
    if MANIFEST_FILE.exists():
        return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    return {"status": "no_cycle_yet"}
