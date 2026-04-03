from fastapi import APIRouter, Body
from pathlib import Path
from datetime import datetime, timezone
import json, uuid, re

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
WORKFLOW_DIR = DATA_DIR / "workflows"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)

WORKFLOWS_FILE = WORKFLOW_DIR / "workflows.json"
RUNS_FILE = WORKFLOW_DIR / "workflow_runs.json"

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
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "workflow")).strip("_")[:80] or "workflow"

def _load_workflows():
    data = _read_json(WORKFLOWS_FILE, {"workflows": []})
    if not isinstance(data, dict):
        data = {"workflows": []}
    data.setdefault("workflows", [])
    return data

def _save_workflows(data: dict):
    _write_json(WORKFLOWS_FILE, data)

def _load_runs():
    data = _read_json(RUNS_FILE, {"runs": []})
    if not isinstance(data, dict):
        data = {"runs": []}
    data.setdefault("runs", [])
    return data

def _save_runs(data: dict):
    _write_json(RUNS_FILE, data)

def _append_run(entry: dict):
    data = _load_runs()
    data["runs"].append(entry)
    data["runs"] = data["runs"][-300:]
    _save_runs(data)
    return entry

def _write_output(name: str, data: dict):
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return f"/api/file/{name}"

def _infer_workflow_type(prompt: str):
    p = (prompt or "").lower()
    if any(x in p for x in ["image", "visual", "screenshot", "thumbnail", "photo"]):
        return "vision"
    if any(x in p for x in ["money", "offer", "sales", "gumroad", "price", "monetize"]):
        return "monetization"
    if any(x in p for x in ["winner", "evolve", "improve", "iterate"]):
        return "evolution"
    if any(x in p for x in ["live", "multimodal", "session"]):
        return "live"
    if any(x in p for x in ["browser", "website", "page", "competitor", "scan"]):
        return "browser"
    return "content"

def _infer_nodes(prompt: str):
    p = (prompt or "").lower()
    nodes = []

    if any(x in p for x in ["image", "visual", "screenshot", "thumbnail", "photo"]):
        nodes.append({"id": "vision_ingest", "kind": "vision", "route": "/api/vision/from-base64", "label": "Vision Ingest"})
        nodes.append({"id": "vision_inspect", "kind": "vision", "route": "/api/vision/inspect", "label": "Visual Inspection"})

    if any(x in p for x in ["competitor", "website", "landing page", "page", "scan"]):
        nodes.append({"id": "browser_scan", "kind": "browser", "route": "/api/operator/browser/scan-and-route", "label": "Browser Scan"})
        nodes.append({"id": "competitor_scan", "kind": "analysis", "route": "/api/vision/competitor-scan", "label": "Competitor Analysis"})

    if any(x in p for x in ["live", "multimodal", "session"]):
        nodes.append({"id": "live_start", "kind": "live", "route": "/api/live/start", "label": "Start Live Session"})
        nodes.append({"id": "live_generate", "kind": "live", "route": "/api/live/generate", "label": "Generate From Session"})

    if any(x in p for x in ["winner", "evolve", "improve", "iterate"]):
        nodes.append({"id": "winner_cycle", "kind": "evolution", "route": "/api/founder/run-winner-cycle", "label": "Winner Cycle"})
        nodes.append({"id": "intel_evolve", "kind": "intelligence", "route": "/api/intel/evolve", "label": "Intelligence Evolve"})
        nodes.append({"id": "learning_memory", "kind": "learning", "route": "/api/learning/evolve-from-memory", "label": "Memory Evolution"})

    if any(x in p for x in ["money", "offer", "sales", "gumroad", "price", "monetize"]):
        nodes.append({"id": "money_generate", "kind": "content", "route": "/api/founder/full-stack-generate", "label": "Full Stack Generate"})
        nodes.append({"id": "monetize_package", "kind": "monetization", "route": "/api/monetize/package", "label": "Monetize Package"})

    if not nodes:
        nodes.append({"id": "money_generate", "kind": "content", "route": "/api/founder/full-stack-generate", "label": "Full Stack Generate"})

    nodes.append({"id": "eval_run", "kind": "eval", "route": "/api/eval/run", "label": "Evaluate Output"})
    return nodes

def _link_nodes(nodes):
    edges = []
    for i in range(len(nodes) - 1):
        edges.append({
            "from": nodes[i]["id"],
            "to": nodes[i + 1]["id"]
        })
    return edges

def _make_workflow(prompt: str, title: str = ""):
    wf_type = _infer_workflow_type(prompt)
    nodes = _infer_nodes(prompt)
    edges = _link_nodes(nodes)

    workflow = {
        "id": f"wf_{uuid.uuid4().hex[:10]}",
        "title": title or f"{wf_type.title()} Workflow",
        "prompt": prompt,
        "workflow_type": wf_type,
        "created_at": _now(),
        "updated_at": _now(),
        "nodes": nodes,
        "edges": edges,
        "status": "active"
    }
    return workflow

def _save_workflow(workflow: dict):
    data = _load_workflows()
    data["workflows"].append(workflow)
    data["workflows"] = data["workflows"][-200:]
    _save_workflows(data)
    return workflow

def _get_workflow(workflow_id: str):
    data = _load_workflows()
    for wf in data.get("workflows", []):
        if wf.get("id") == workflow_id:
            return wf
    return None

def _safe_topic(payload: dict, fallback: str):
    return payload.get("topic") or payload.get("title") or fallback

def _execute_node(node: dict, payload: dict):
    route = node.get("route", "")
    kind = node.get("kind", "")
    label = node.get("label", route)

    try:
        if route == "/api/founder/full-stack-generate":
            from backend.app.money_sweep import founder_full_stack_generate
            result = founder_full_stack_generate({
                "topic": _safe_topic(payload, "Workflow Topic"),
                "buyer": payload.get("buyer", "Creators"),
                "promise": payload.get("promise", "move faster"),
                "niche": payload.get("niche", "Content Monetization"),
                "tone": payload.get("tone", "Premium"),
                "bonus": payload.get("bonus", "workflow builder bonus"),
                "notes": payload.get("notes", "workflow builder execution")
            })
            return {"status": "ok", "label": label, "route": route, "result": result}

        if route == "/api/monetize/package":
            from backend.app.monetization import monetize_package
            result = monetize_package({
                "topic": _safe_topic(payload, "Workflow Topic"),
                "buyer": payload.get("buyer", "Creators"),
                "promise": payload.get("promise", "make money faster"),
                "niche": payload.get("niche", "Content Monetization"),
                "tone": payload.get("tone", "Premium"),
                "bonus": payload.get("bonus", "workflow pricing bonus"),
                "notes": payload.get("notes", "workflow monetization")
            })
            return {"status": "ok", "label": label, "route": route, "result": result}

        if route == "/api/founder/run-winner-cycle":
            from backend.app.winner_cycle import run_winner_cycle
            result = run_winner_cycle({
                "topic": _safe_topic(payload, "Workflow Topic"),
                "buyer": payload.get("buyer", "Creators"),
                "promise": payload.get("promise", "grow faster"),
                "niche": payload.get("niche", "Content Monetization"),
                "notes": payload.get("notes", "workflow winner cycle")
            })
            return {"status": "ok", "label": label, "route": route, "result": result}

        if route == "/api/intel/evolve":
            from backend.app.intelligence import intel_evolve
            result = intel_evolve({
                "topic": _safe_topic(payload, "Workflow Topic"),
                "buyer": payload.get("buyer", "Creators"),
                "promise": payload.get("promise", "grow faster"),
                "niche": payload.get("niche", "Content Monetization"),
                "tone": payload.get("tone", "Premium"),
                "bonus": payload.get("bonus", "workflow intelligence bonus")
            })
            return {"status": "ok", "label": label, "route": route, "result": result}

        if route == "/api/learning/evolve-from-memory":
            from backend.app.learning import learning_evolve_from_memory
            result = learning_evolve_from_memory({
                "topic": _safe_topic(payload, "Workflow Topic"),
                "buyer": payload.get("buyer", "Creators"),
                "promise": payload.get("promise", "grow faster"),
                "niche": payload.get("niche", "Content Monetization"),
                "tone": payload.get("tone", "Premium"),
                "bonus": payload.get("bonus", "workflow memory bonus")
            })
            return {"status": "ok", "label": label, "route": route, "result": result}

        if route == "/api/vision/competitor-scan":
            from backend.app.vision_hardening import competitor_scan
            result = competitor_scan({
                "text": payload.get("text", payload.get("topic", "workflow competitor scan")),
                "topic": _safe_topic(payload, "Workflow Topic")
            })
            return {"status": "ok", "label": label, "route": route, "result": result}

        if route == "/api/operator/browser/scan-and-route":
            from backend.app.browser_operator import browser_scan_and_route
            result = browser_scan_and_route({
                "url": payload.get("url", "https://example.com"),
                "topic": _safe_topic(payload, "Workflow Topic"),
                "text": payload.get("text", ""),
                "notes": payload.get("notes", "workflow browser scan")
            })
            return {"status": "ok", "label": label, "route": route, "result": result}

        if route == "/api/live/start":
            from backend.app.live_mode import live_start
            result = live_start({"mode": "workflow"})
            return {"status": "ok", "label": label, "route": route, "result": result}

        if route == "/api/live/generate":
            return {"status": "ok", "label": label, "route": route, "result": {"message": "live generate requires an existing live session"}}

        if route == "/api/eval/run":
            from backend.app.evals import run_eval
            eval_text = payload.get("text") or payload.get("topic") or "workflow output"
            result = run_eval({
                "text": eval_text,
                "name": payload.get("title", "workflow_eval")
            })
            return {"status": "ok", "label": label, "route": route, "result": result}

        return {"status": "ok", "label": label, "route": route, "result": {"message": "node simulated", "kind": kind}}

    except Exception as e:
        return {"status": "error", "label": label, "route": route, "error": str(e)}

@router.post("/api/workflow/build")
def workflow_build(payload: dict = Body(...)):
    prompt = payload.get("prompt", "")
    title = payload.get("title", "")
    workflow = _make_workflow(prompt, title=title)
    _save_workflow(workflow)

    artifact_url = _write_output(
        f"{_slug(workflow['title'])}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_workflow.json",
        workflow
    )

    return {
        "status": "ok",
        "phase": "natural-language workflow builder",
        "workflow": workflow,
        "artifact_url": artifact_url
    }

@router.post("/api/workflow/run")
def workflow_run(payload: dict = Body(...)):
    workflow_id = payload.get("workflow_id", "")
    workflow = _get_workflow(workflow_id)
    if not workflow:
        return {"status": "error", "error": "workflow not found"}

    run_id = f"wfrun_{uuid.uuid4().hex[:10]}"
    run_payload = payload.get("payload", {})
    results = []

    for node in workflow.get("nodes", []):
        result = _execute_node(node, run_payload)
        results.append({
            "node_id": node.get("id"),
            "label": node.get("label"),
            "route": node.get("route"),
            "status": result.get("status"),
            "result": result.get("result"),
            "error": result.get("error", "")
        })

    success_count = len([r for r in results if r.get("status") == "ok"])
    error_count = len([r for r in results if r.get("status") == "error"])

    run_record = {
        "id": run_id,
        "workflow_id": workflow_id,
        "workflow_title": workflow.get("title", ""),
        "time": _now(),
        "payload": run_payload,
        "results": results,
        "success_count": success_count,
        "error_count": error_count,
        "status": "completed" if error_count == 0 else "completed_with_errors"
    }

    _append_run(run_record)

    artifact_url = _write_output(
        f"{_slug(workflow.get('title','workflow'))}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_workflow_run.json",
        run_record
    )

    return {
        "status": "ok",
        "phase": "natural-language workflow builder",
        "run": run_record,
        "artifact_url": artifact_url
    }

@router.get("/api/workflow/status")
def workflow_status():
    workflows = _load_workflows()
    runs = _load_runs()

    wf_list = workflows.get("workflows", [])
    run_list = runs.get("runs", [])

    return {
        "status": "ok",
        "phase": "natural-language workflow builder",
        "counts": {
            "workflows": len(wf_list),
            "runs": len(run_list)
        },
        "recent_workflows": sorted(wf_list, key=lambda x: x.get("updated_at", x.get("created_at", "")), reverse=True)[:12],
        "recent_runs": sorted(run_list, key=lambda x: x.get("time", ""), reverse=True)[:12]
    }

@router.get("/api/workflow/{workflow_id}")
def workflow_get(workflow_id: str):
    workflow = _get_workflow(workflow_id)
    if not workflow:
        return {"status": "error", "error": "workflow not found"}
    return {
        "status": "ok",
        "phase": "natural-language workflow builder",
        "workflow": workflow
    }

@router.post("/api/workflow/quick-build-and-run")
def workflow_quick_build_and_run(payload: dict = Body(...)):
    prompt = payload.get("prompt", "")
    title = payload.get("title", "")
    run_payload = payload.get("payload", {})

    workflow = _make_workflow(prompt, title=title)
    _save_workflow(workflow)

    results = []
    for node in workflow.get("nodes", []):
        result = _execute_node(node, run_payload)
        results.append({
            "node_id": node.get("id"),
            "label": node.get("label"),
            "route": node.get("route"),
            "status": result.get("status"),
            "result": result.get("result"),
            "error": result.get("error", "")
        })

    run_record = {
        "id": f"wfrun_{uuid.uuid4().hex[:10]}",
        "workflow_id": workflow["id"],
        "workflow_title": workflow.get("title", ""),
        "time": _now(),
        "payload": run_payload,
        "results": results,
        "success_count": len([r for r in results if r.get("status") == "ok"]),
        "error_count": len([r for r in results if r.get("status") == "error"]),
        "status": "completed_with_errors" if any(r.get("status") == "error" for r in results) else "completed"
    }

    _append_run(run_record)

    artifact_url = _write_output(
        f"{_slug(workflow.get('title','workflow'))}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_workflow_quick_run.json",
        {
            "workflow": workflow,
            "run": run_record
        }
    )

    return {
        "status": "ok",
        "phase": "natural-language workflow builder",
        "workflow": workflow,
        "run": run_record,
        "artifact_url": artifact_url
    }
