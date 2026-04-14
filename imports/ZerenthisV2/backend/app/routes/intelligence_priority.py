from pathlib import Path
import json
from fastapi import APIRouter
from backend.app.engines.intelligence_priority_engine import run_priority_engine

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "backend" / "data"
CURRENT_TOPIC_FILE = DATA_DIR / "current_topic.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/api/intelligence/priority")
def run_priority():
    result = run_priority_engine()
    top = result.get("top_target") or {}

    if top.get("topic"):
        CURRENT_TOPIC_FILE.write_text(
            json.dumps(
                {
                    "topic": top.get("topic"),
                    "source": top.get("source"),
                    "revenue": top.get("revenue", 0),
                    "conversions": top.get("conversions", 0),
                    "total_score": top.get("total_score", 0),
                    "locked_at": result.get("timestamp")
                },
                indent=2
            ),
            encoding="utf-8"
        )

    return {
        "status": "priority_generated",
        "candidate_count": result.get("candidate_count", 0),
        "top_target": top,
        "top_3": result.get("ranked", [])[:3],
        "locked_topic_file": "backend/data/current_topic.json",
        "file": "backend/data/ranked_targets.json"
    }
