from __future__ import annotations

from fastapi import APIRouter, HTTPException
from collections import Counter
import json
from pathlib import Path



router = APIRouter(prefix="/api/self-improver", tags=["self-improver"])

ROOT = Path(__file__).resolve().parents[2]
EXECUTION_LOG = ROOT / "backend" / "data" / "self_improver" / "execution_log.json"

def _load_execution_log():
    if not EXECUTION_LOG.exists():
        return []
    try:
        data = json.loads(EXECUTION_LOG.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

@router.get("/health")
def self_improver_health():
    return {"ok": True, "verified": verify()}

@router.get("/proposals")
def list_pending_proposals():
    return {"items": pending()}

@router.get("/applied")
def list_applied_proposals():
    return {"items": applied()}

@router.get("/failed")
def list_failed_proposals():
    return {"items": failed()}

@router.get("/history")
def history():
    items = load()
    return {"items": sorted(items, key=lambda x: x.get("created_ts", 0), reverse=True)}

@router.get("/stats")
def stats():
    items = load()
    executions = _load_execution_log()
    status_counts = Counter(item.get("status", "unknown") for item in items)
    execution_counts = Counter(item.get("status", "unknown") for item in executions)
    return {
        "total": len(items),
        "proposal_statuses": dict(status_counts),
        "execution_statuses": dict(execution_counts),
        "approval_rate_percent": round(((status_counts.get("approved", 0) + status_counts.get("applied", 0) + status_counts.get("failed", 0)) / len(items)) * 100, 2) if items else 0.0,
    }

@router.post("/approve/{proposal_id}")
def approve_proposal(proposal_id: str):
    ok = approve(proposal_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {"ok": True, "id": proposal_id, "status": "approved"}

@router.post("/reject/{proposal_id}")
def reject_proposal(proposal_id: str):
    ok = reject(proposal_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {"ok": True, "id": proposal_id, "status": "rejected"}

@router.post("/execute/{proposal_id}")
def execute_proposal(proposal_id: str):
    result = execute(proposal_id)
    if result.get("error") == "not approved":
        raise HTTPException(status_code=400, detail="Proposal is not approved")
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "Execution failed"))
    return result


