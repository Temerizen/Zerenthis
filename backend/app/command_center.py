from fastapi import APIRouter, Body
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/command", tags=["command"])

def _now():
    return datetime.now(timezone.utc).isoformat()

def _safe_dict(x):
    return x if isinstance(x, dict) else {"value": x}

@router.post("/run")
def run_command(payload: dict = Body(...)):
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return {"status": "error", "error": "prompt is required"}

    trace = []
    knowledge = {}
    workflow = {}
    summary_bits = []
    assets = []

    try:
        from backend.app.knowledge import knowledge_apply
        knowledge = _safe_dict(knowledge_apply({
            "query": prompt,
            "topic": prompt,
            "buyer": payload.get("buyer", "Creators"),
            "niche": payload.get("niche", "Content Monetization"),
            "promise": payload.get("promise", "move faster")
        }))
        trace.append("knowledge_apply:ok")

        guidance = _safe_dict(knowledge.get("guidance", {}))
        if guidance.get("guided_topic"):
            summary_bits.append(f"Guided topic: {guidance['guided_topic']}")
        if knowledge.get("artifact_url"):
            assets.append({
                "type": "knowledge_artifact",
                "label": "Knowledge Artifact",
                "url": knowledge.get("artifact_url")
            })
    except Exception as e:
        knowledge = {"status": "error", "error": str(e)}
        trace.append(f"knowledge_apply:error:{e}")

    try:
        from backend.app.workflow_builder import workflow_quick_build_and_run
        workflow = _safe_dict(workflow_quick_build_and_run({
            "prompt": prompt,
            "title": f"Apple Flow: {prompt[:60]}",
            "payload": {
                "topic": prompt,
                "text": prompt,
                "buyer": payload.get("buyer", "Creators"),
                "niche": payload.get("niche", "Content Monetization"),
                "promise": payload.get("promise", "move faster"),
                "bonus": payload.get("bonus", "apple command bonus"),
                "notes": payload.get("notes", "apple command center execution"),
                "url": payload.get("url", "")
            }
        }))
        trace.append("workflow_quick_build_and_run:ok")

        run = _safe_dict(workflow.get("run", {}))
        if run.get("status"):
            summary_bits.append(f"Workflow status: {run['status']}")
        if workflow.get("artifact_url"):
            assets.append({
                "type": "workflow_artifact",
                "label": "Workflow Artifact",
                "url": workflow.get("artifact_url")
            })
    except Exception as e:
        workflow = {"status": "error", "error": str(e)}
        trace.append(f"workflow_quick_build_and_run:error:{e}")

    title = f"Zerenthis Command Result: {prompt}"
    summary = " | ".join(summary_bits) if summary_bits else "Command executed through Apple command center."

    return {
        "status": "ok",
        "phase": "apple command center",
        "job_id": f"cmd_{uuid.uuid4().hex[:10]}",
        "created_at": _now(),
        "input": {
            "prompt": prompt,
            "buyer": payload.get("buyer", "Creators"),
            "niche": payload.get("niche", "Content Monetization"),
            "promise": payload.get("promise", "move faster")
        },
        "result": {
            "title": title,
            "summary": summary,
            "assets": assets,
            "next_action": "Connect this route to the frontend single-input Apple panel."
        },
        "modules": {
            "knowledge": knowledge,
            "workflow": workflow
        },
        "trace": trace
    }
