from fastapi import APIRouter, Body
from pathlib import Path
from datetime import datetime, timezone
import json, uuid, re

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
BROWSER_DIR = DATA_DIR / "browser_ops"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BROWSER_DIR.mkdir(parents=True, exist_ok=True)

OPS_FILE = BROWSER_DIR / "operations.json"
APPROVALS_FILE = BROWSER_DIR / "approvals.json"

def _now():
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "operator")).strip("_")[:80] or "operator"

def _safe_host(url: str):
    m = re.match(r"^https?://([^/]+)", (url or "").strip().lower())
    return m.group(1) if m else ""

def _classify_risk(action: dict):
    url = (action.get("url") or "").lower()
    op = (action.get("operation") or "").lower()
    text = (action.get("text") or "").lower()

    if any(x in op for x in ["delete", "remove", "purchase", "buy", "pay", "submit", "checkout", "transfer"]):
        return "high"
    if any(x in text for x in ["password", "credit card", "ssn", "sin", "bank", "2fa", "otp"]):
        return "high"
    if any(x in url for x in ["mail.google.com", "bank", "checkout", "billing", "ads.google.com"]):
        return "high"
    if any(x in op for x in ["type", "fill", "click", "post", "publish"]):
        return "medium"
    return "low"

def _load_ops():
    data = _read_json(OPS_FILE, {"operations": []})
    if not isinstance(data, dict):
        data = {"operations": []}
    data.setdefault("operations", [])
    return data

def _save_ops(data: dict):
    _write_json(OPS_FILE, data)

def _load_approvals():
    data = _read_json(APPROVALS_FILE, {"pending": [], "history": []})
    if not isinstance(data, dict):
        data = {"pending": [], "history": []}
    data.setdefault("pending", [])
    data.setdefault("history", [])
    return data

def _save_approvals(data: dict):
    _write_json(APPROVALS_FILE, data)

def _append_operation(entry: dict):
    data = _load_ops()
    data["operations"].append(entry)
    data["operations"] = data["operations"][-500:]
    _save_ops(data)
    return entry

def _queue_approval(action: dict, reason: str):
    approvals = _load_approvals()
    item = {
        "id": f"browser_approval_{uuid.uuid4().hex[:10]}",
        "created_at": _now(),
        "status": "pending",
        "reason": reason,
        "action": action,
        "risk": _classify_risk(action)
    }
    approvals["pending"].append(item)
    approvals["pending"] = approvals["pending"][-200:]
    _save_approvals(approvals)
    return item

def _approve(approval_id: str):
    approvals = _load_approvals()
    pending = approvals.get("pending", [])
    item = next((x for x in pending if x.get("id") == approval_id), None)
    if not item:
        return None
    item["status"] = "approved"
    item["approved_at"] = _now()
    approvals["pending"] = [x for x in pending if x.get("id") != approval_id]
    approvals["history"].append(item)
    approvals["history"] = approvals["history"][-500:]
    _save_approvals(approvals)
    return item

def _reject(approval_id: str):
    approvals = _load_approvals()
    pending = approvals.get("pending", [])
    item = next((x for x in pending if x.get("id") == approval_id), None)
    if not item:
        return None
    item["status"] = "rejected"
    item["rejected_at"] = _now()
    approvals["pending"] = [x for x in pending if x.get("id") != approval_id]
    approvals["history"].append(item)
    approvals["history"] = approvals["history"][-500:]
    _save_approvals(approvals)
    return item

def _simulate_browser_action(action: dict):
    url = action.get("url", "")
    operation = action.get("operation", "open")
    selector = action.get("selector", "")
    text = action.get("text", "")
    topic = action.get("topic", "")

    host = _safe_host(url)
    result = {
        "time": _now(),
        "mode": "simulated_browser_operator",
        "host": host,
        "url": url,
        "operation": operation,
        "selector": selector,
        "text_preview": text[:180],
        "topic": topic,
        "summary": f"Simulated {operation} on {host or 'unknown host'}",
        "next_best_step": "review outcome and escalate only after founder approval"
    }

    if operation in ("analyze_page", "scan_offer", "extract"):
        result["extracted"] = {
            "headline_angle": "clarity + speed + monetization",
            "weaknesses": ["needs stronger differentiation", "CTA could be clearer"],
            "opportunities": ["add stronger promise", "tighten buyer targeting", "expand proof"]
        }

    return result

def _write_output(name: str, data: dict):
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

@router.post("/api/operator/browser/request")
def browser_request(payload: dict = Body(...)):
    action = {
        "id": f"browser_op_{uuid.uuid4().hex[:10]}",
        "created_at": _now(),
        "url": payload.get("url", ""),
        "operation": payload.get("operation", "open"),
        "selector": payload.get("selector", ""),
        "text": payload.get("text", ""),
        "topic": payload.get("topic", ""),
        "notes": payload.get("notes", "")
    }

    risk = _classify_risk(action)
    action["risk"] = risk

    if risk in ("high", "medium"):
        approval = _queue_approval(action, f"{risk.title()}-risk browser action requires founder approval")
        _append_operation({
            "time": _now(),
            "status": "queued_for_approval",
            "action": action,
            "approval_id": approval["id"]
        })
        return {
            "status": "queued_for_approval",
            "phase": "browser operator + approval gates",
            "approval": approval
        }

    result = _simulate_browser_action(action)
    artifact_url = _write_output(f"{_slug(action.get('topic') or action.get('operation'))}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_browser.json", result)
    _append_operation({
        "time": _now(),
        "status": "executed",
        "action": action,
        "result": result,
        "artifact_url": artifact_url
    })

    return {
        "status": "executed",
        "phase": "browser operator + approval gates",
        "risk": risk,
        "result": result,
        "artifact_url": artifact_url
    }

@router.post("/api/operator/browser/approve")
def browser_approve(payload: dict = Body(...)):
    approval_id = payload.get("id", "")
    item = _approve(approval_id)
    if not item:
        return {"status": "error", "error": "approval not found"}

    action = item.get("action", {})
    result = _simulate_browser_action(action)
    artifact_url = _write_output(f"{_slug(action.get('topic') or action.get('operation'))}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_browser.json", result)

    _append_operation({
        "time": _now(),
        "status": "executed_after_approval",
        "action": action,
        "approval_id": approval_id,
        "result": result,
        "artifact_url": artifact_url
    })

    return {
        "status": "ok",
        "phase": "browser operator + approval gates",
        "approved": item,
        "result": result,
        "artifact_url": artifact_url
    }

@router.post("/api/operator/browser/reject")
def browser_reject(payload: dict = Body(...)):
    approval_id = payload.get("id", "")
    item = _reject(approval_id)
    if not item:
        return {"status": "error", "error": "approval not found"}
    _append_operation({
        "time": _now(),
        "status": "rejected",
        "action": item.get("action", {}),
        "approval_id": approval_id
    })
    return {
        "status": "ok",
        "phase": "browser operator + approval gates",
        "rejected": item
    }

@router.get("/api/operator/browser/status")
def browser_status():
    ops = _load_ops()
    approvals = _load_approvals()
    operations = ops.get("operations", [])

    return {
        "status": "ok",
        "phase": "browser operator + approval gates",
        "counts": {
            "operations": len(operations),
            "pending_approvals": len(approvals.get("pending", [])),
            "approval_history": len(approvals.get("history", []))
        },
        "recent_operations": operations[-15:],
        "pending_approvals": approvals.get("pending", [])[-15:],
        "approval_history": approvals.get("history", [])[-15:]
    }

@router.post("/api/operator/browser/scan-and-route")
def browser_scan_and_route(payload: dict = Body(...)):
    url = payload.get("url", "")
    topic = payload.get("topic", "browser scan target")
    action = {
        "url": url,
        "operation": "analyze_page",
        "selector": payload.get("selector", "body"),
        "text": payload.get("text", ""),
        "topic": topic,
        "notes": payload.get("notes", "scan and route")
    }

    result = _simulate_browser_action(action)
    extracted = (result.get("extracted") or {})
    recommendation = {
        "route": "/api/vision/competitor-scan",
        "reason": "page-analysis style extraction is best handled by competitor scan layer",
        "topic": topic,
        "opportunities": extracted.get("opportunities", [])
    }

    artifact_url = _write_output(f"{_slug(topic)}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_scan_route.json", {
        "time": _now(),
        "phase": "browser operator + approval gates",
        "action": action,
        "result": result,
        "recommendation": recommendation
    })

    _append_operation({
        "time": _now(),
        "status": "scanned_and_routed",
        "action": action,
        "result": result,
        "recommendation": recommendation,
        "artifact_url": artifact_url
    })

    return {
        "status": "ok",
        "phase": "browser operator + approval gates",
        "result": result,
        "recommendation": recommendation,
        "artifact_url": artifact_url
    }
