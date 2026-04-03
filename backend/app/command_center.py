from fastapi import APIRouter
from pathlib import Path
from datetime import datetime, timezone
import json, os

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SECTIONS = {
    "system": DATA_DIR / "health.json",
    "autopilot": DATA_DIR / "autopilot_state.json",
    "approvals": DATA_DIR / "approvals.json",
    "browser_ops": DATA_DIR / "browser_ops" / "operations.json",
    "browser_approvals": DATA_DIR / "browser_ops" / "approvals.json",
    "tasks": DATA_DIR / "tasks" / "queue.json",
    "projects": DATA_DIR / "tasks" / "projects.json",
    "workflows": DATA_DIR / "workflows" / "workflows.json",
    "workflow_runs": DATA_DIR / "workflows" / "workflow_runs.json",
    "knowledge_packs": DATA_DIR / "knowledge" / "packs.json",
    "knowledge_memory": DATA_DIR / "knowledge" / "memory.json",
    "knowledge_rankings": DATA_DIR / "knowledge" / "rankings.json",
    "learning_patterns": DATA_DIR / "learning_patterns.json",
    "anomalies": DATA_DIR / "anomalies.json",
    "winners": DATA_DIR / "winners.json",
    "blacklist": DATA_DIR / "blacklist.json",
    "pricing_rules": DATA_DIR / "pricing_rules.json"
}

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

def _recent_outputs(limit=20):
    items = []
    if OUTPUT_DIR.exists():
        for p in OUTPUT_DIR.iterdir():
            if p.is_file():
                try:
                    s = p.stat()
                    items.append({
                        "name": p.name,
                        "size": s.st_size,
                        "modified_at": datetime.fromtimestamp(s.st_mtime, tz=timezone.utc).isoformat(),
                        "url": f"/api/file/{p.name}"
                    })
                except Exception:
                    pass
    items.sort(key=lambda x: x["modified_at"], reverse=True)
    return items[:limit]

def _safe_len(obj, key=None):
    if key is not None and isinstance(obj, dict):
        obj = obj.get(key, [])
    if isinstance(obj, list):
        return len(obj)
    if isinstance(obj, dict):
        return len(obj)
    return 0

def _summary():
    data = {name: _read_json(path, {}) for name, path in SECTIONS.items()}

    tasks = data.get("tasks", {}).get("tasks", []) if isinstance(data.get("tasks", {}), dict) else []
    projects = data.get("projects", {}).get("projects", []) if isinstance(data.get("projects", {}), dict) else []
    workflows = data.get("workflows", {}).get("workflows", []) if isinstance(data.get("workflows", {}), dict) else []
    workflow_runs = data.get("workflow_runs", {}).get("runs", []) if isinstance(data.get("workflow_runs", {}), dict) else []
    packs = data.get("knowledge_packs", {}).get("packs", []) if isinstance(data.get("knowledge_packs", {}), dict) else []
    memory_items = data.get("knowledge_memory", {}).get("items", []) if isinstance(data.get("knowledge_memory", {}), dict) else []
    ranking_history = data.get("knowledge_rankings", {}).get("history", []) if isinstance(data.get("knowledge_rankings", {}), dict) else []
    browser_ops = data.get("browser_ops", {}).get("operations", []) if isinstance(data.get("browser_ops", {}), dict) else []
    browser_pending = data.get("browser_approvals", {}).get("pending", []) if isinstance(data.get("browser_approvals", {}), dict) else []
    approvals_pending = data.get("approvals", {}).get("pending", []) if isinstance(data.get("approvals", {}), dict) else []
    approvals_history = data.get("approvals", {}).get("history", []) if isinstance(data.get("approvals", {}), dict) else []
    winners = data.get("winners", [])
    if isinstance(winners, dict):
        winners = winners.get("winners", [])
    blacklist = data.get("blacklist", [])
    if isinstance(blacklist, dict):
        blacklist = blacklist.get("items", [])

    queued = len([t for t in tasks if str(t.get("status","")).lower() == "queued"])
    running = len([t for t in tasks if str(t.get("status","")).lower() == "running"])
    completed = len([t for t in tasks if str(t.get("status","")).lower() == "completed"])
    failed = len([t for t in tasks if str(t.get("status","")).lower() == "failed"])

    autopilot = data.get("autopilot", {}) if isinstance(data.get("autopilot", {}), dict) else {}
    system = data.get("system", {}) if isinstance(data.get("system", {}), dict) else {}
    learning = data.get("learning_patterns", {}) if isinstance(data.get("learning_patterns", {}), dict) else {}
    anomalies = data.get("anomalies", [])
    if isinstance(anomalies, dict):
        anomalies = anomalies.get("items", [])

    status = {
        "generated_at": _now(),
        "phase": "founder command center",
        "command_center": {
            "system_ok": bool(system) or OUTPUT_DIR.exists(),
            "autopilot_enabled": bool(autopilot.get("enabled", False)),
            "autopilot_mode": autopilot.get("mode", "safe"),
            "last_run_at": autopilot.get("last_run_at", ""),
            "last_result": autopilot.get("last_result", "")
        },
        "counts": {
            "tasks_queued": queued,
            "tasks_running": running,
            "tasks_completed": completed,
            "tasks_failed": failed,
            "projects": len(projects),
            "workflows": len(workflows),
            "workflow_runs": len(workflow_runs),
            "knowledge_packs": len(packs),
            "memory_items": len(memory_items),
            "ranking_history": len(ranking_history),
            "browser_operations": len(browser_ops),
            "browser_pending_approvals": len(browser_pending),
            "autopilot_pending_approvals": len(approvals_pending),
            "autopilot_approval_history": len(approvals_history),
            "winners": len(winners) if isinstance(winners, list) else 0,
            "blacklist": len(blacklist) if isinstance(blacklist, list) else 0,
            "learning_runs": int(learning.get("runs", 0)) if isinstance(learning, dict) else 0,
            "recent_anomalies": len(anomalies) if isinstance(anomalies, list) else 0
        },
        "top_signals": {
            "winning_keywords": sorted((learning.get("winning_keywords", {}) if isinstance(learning, dict) else {}).items(), key=lambda x: x[1], reverse=True)[:10],
            "losing_keywords": sorted((learning.get("losing_keywords", {}) if isinstance(learning, dict) else {}).items(), key=lambda x: x[1], reverse=True)[:10],
            "top_packs": [
                {
                    "name": p.get("name", ""),
                    "niche": p.get("niche", ""),
                    "buyer": p.get("buyer", "")
                } for p in packs[-10:]
            ] if isinstance(packs, list) else []
        },
        "recent_outputs": _recent_outputs(20),
        "next_actions": [
            {"label": "Generate", "route": "/api/founder/full-stack-generate"},
            {"label": "Monetize", "route": "/api/monetize/package"},
            {"label": "Winner Cycle", "route": "/api/founder/run-winner-cycle"},
            {"label": "Autopilot Status", "route": "/api/autopilot/status"},
            {"label": "Inbox Status", "route": "/api/inbox/status"},
            {"label": "Workflow Status", "route": "/api/workflow/status"},
            {"label": "Knowledge Status", "route": "/api/knowledge/status"},
            {"label": "Command Center", "route": "/api/founder/command-center"}
        ]
    }
    return status

@router.get("/api/founder/command-center")
def founder_command_center():
    status = _summary()
    return {
        "status": "ok",
        "phase": "founder command center",
        "dashboard": status
    }

@router.get("/api/founder/launch-readiness")
def founder_launch_readiness():
    status = _summary()
    counts = status.get("counts", {})
    score = 0

    if status["command_center"]["system_ok"]:
        score += 15
    if counts.get("tasks_completed", 0) >= 1:
        score += 10
    if counts.get("workflows", 0) >= 1:
        score += 10
    if counts.get("knowledge_packs", 0) >= 1:
        score += 10
    if counts.get("memory_items", 0) >= 3:
        score += 10
    if counts.get("winners", 0) >= 1:
        score += 10
    if len(status.get("recent_outputs", [])) >= 3:
        score += 15
    if counts.get("workflow_runs", 0) >= 1:
        score += 10
    if counts.get("tasks_failed", 0) == 0:
        score += 10

    readiness = min(score, 100)
    verdict = "launch_ready" if readiness >= 80 else ("almost_ready" if readiness >= 60 else "still_building")

    return {
        "status": "ok",
        "phase": "founder command center",
        "readiness_score": readiness,
        "verdict": verdict,
        "signals": status
    }

@router.post("/api/founder/mission-brief")
def founder_mission_brief():
    status = _summary()
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    artifact = {
        "time": _now(),
        "phase": "founder command center",
        "brief": status
    }
    artifact_url = f"/api/file/founder_mission_brief_{stamp}.json"
    _write_json(OUTPUT_DIR / f"founder_mission_brief_{stamp}.json", artifact)
    return {
        "status": "ok",
        "phase": "founder command center",
        "artifact_url": artifact_url,
        "brief": artifact
    }

@router.get("/api/founder/empire-status")
def founder_empire_status():
    status = _summary()
    counts = status.get("counts", {})
    systems = {
        "generation": True,
        "monetization": True,
        "winner_cycle": True,
        "autopilot": True,
        "vision": True,
        "live_mode": True,
        "workflow_builder": True,
        "knowledge_engine": True,
        "browser_operator": True,
        "durable_inbox": True,
        "evals_and_traces": True
    }
    return {
        "status": "ok",
        "phase": "founder command center",
        "empire": {
            "systems": systems,
            "counts": counts,
            "recent_outputs": status.get("recent_outputs", [])[:10],
            "autopilot": status.get("command_center", {})
        }
    }
