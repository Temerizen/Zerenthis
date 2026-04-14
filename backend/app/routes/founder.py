from flask import Blueprint, jsonify, request
from backend.simulation.simulation_factory import generate_scenario, get_recent_simulation_runs
from backend.growth.growth_factory import generate_growth_plan, get_recent_growth_runs
from backend.auth.founder_guard import founder_access_granted
from backend.founder.event_log import log_founder_event, get_founder_events
from backend.founder.report_factory import generate_founder_report
from backend.dashboards.founder_snapshot import build_founder_snapshot

founder_bp = Blueprint("founder", __name__)

@founder_bp.post("/simulation/run")
def simulation_run():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    domain = (payload.get("domain") or "").strip()
    objective = (payload.get("objective") or "").strip()
    constraints = payload.get("constraints") or []

    if not name or not domain or not objective:
        return jsonify({"ok": False, "error": "name, domain, and objective are required"}), 400

    if not isinstance(constraints, list):
        return jsonify({"ok": False, "error": "constraints must be a list"}), 400

    result = generate_scenario(name, domain, objective, constraints)
    return jsonify({"ok": True, "result": result})

@founder_bp.get("/simulation/runs")
def simulation_runs():
    return jsonify({"ok": True, "items": get_recent_simulation_runs(limit=100)})

@founder_bp.post("/growth/plan")
def growth_plan():
    payload = request.get_json(silent=True) or {}
    target = (payload.get("target") or "").strip()
    platform = (payload.get("platform") or "").strip()
    cadence = (payload.get("cadence") or "").strip()

    if not target or not platform or not cadence:
        return jsonify({"ok": False, "error": "target, platform, and cadence are required"}), 400

    result = generate_growth_plan(target, platform, cadence)
    return jsonify({"ok": True, "result": result})

@founder_bp.get("/growth/runs")
def growth_runs():
    return jsonify({"ok": True, "items": get_recent_growth_runs(limit=100)})

@founder_bp.get("/founder/status")
def founder_status():
    granted = founder_access_granted()
    return jsonify({
        "ok": True,
        "founder_mode": granted
    })

@founder_bp.get("/founder/dashboard")
def founder_dashboard():
    if not founder_access_granted():
        return jsonify({"ok": False, "error": "founder access required"}), 403

    snapshot = build_founder_snapshot()
    log_founder_event("dashboard_view", snapshot)
    return jsonify({"ok": True, "snapshot": snapshot})

@founder_bp.post("/founder/report")
def founder_report():
    if not founder_access_granted():
        return jsonify({"ok": False, "error": "founder access required"}), 403

    result = generate_founder_report()
    log_founder_event("report_generated", result["snapshot"])
    return jsonify({"ok": True, "result": result})

@founder_bp.get("/founder/events")
def founder_events():
    if not founder_access_granted():
        return jsonify({"ok": False, "error": "founder access required"}), 403

    return jsonify({"ok": True, "items": get_founder_events(limit=100)})

