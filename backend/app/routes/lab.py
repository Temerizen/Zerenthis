from flask import Blueprint, jsonify, request
from backend.education.subjects.catalog import SUBJECT_CATALOG, LEVEL_CATALOG
from backend.education.education_factory import generate_learning_plan, generate_lesson, generate_assessment, generate_subject_pack
from backend.education.run_log import get_recent_education_runs
from backend.cognitive.cognitive_factory import generate_drill, generate_report
from backend.education.run_log import get_recent_cognitive_runs

lab_bp = Blueprint("lab", __name__)

@lab_bp.get("/education/catalog")
def education_catalog():
    return jsonify({
        "ok": True,
        "subjects": SUBJECT_CATALOG,
        "levels": LEVEL_CATALOG
    })

@lab_bp.post("/education/plan")
def education_plan():
    payload = request.get_json(silent=True) or {}
    subject = (payload.get("subject") or "").strip()
    level = (payload.get("level") or "").strip()

    if not subject or not level:
        return jsonify({"ok": False, "error": "subject and level are required"}), 400

    return jsonify({"ok": True, "result": generate_learning_plan(subject, level)})

@lab_bp.post("/education/lesson")
def education_lesson():
    payload = request.get_json(silent=True) or {}
    subject = (payload.get("subject") or "").strip()
    level = (payload.get("level") or "").strip()
    topic = (payload.get("topic") or "").strip()

    if not subject or not level or not topic:
        return jsonify({"ok": False, "error": "subject, level, and topic are required"}), 400

    return jsonify({"ok": True, "result": generate_lesson(subject, level, topic)})

@lab_bp.post("/education/assessment")
def education_assessment():
    payload = request.get_json(silent=True) or {}
    subject = (payload.get("subject") or "").strip()
    level = (payload.get("level") or "").strip()
    topic = (payload.get("topic") or "").strip()

    if not subject or not level or not topic:
        return jsonify({"ok": False, "error": "subject, level, and topic are required"}), 400

    return jsonify({"ok": True, "result": generate_assessment(subject, level, topic)})

@lab_bp.post("/education/subject-pack")
def education_subject_pack():
    payload = request.get_json(silent=True) or {}
    subject = (payload.get("subject") or "").strip()
    level = (payload.get("level") or "").strip()
    topic = (payload.get("topic") or "").strip()

    if not subject or not level or not topic:
        return jsonify({"ok": False, "error": "subject, level, and topic are required"}), 400

    return jsonify({"ok": True, "result": generate_subject_pack(subject, level, topic)})

@lab_bp.get("/education/runs")
def education_runs():
    return jsonify({"ok": True, "items": get_recent_education_runs(limit=100)})

@lab_bp.post("/cognitive/drill")
def cognitive_drill():
    payload = request.get_json(silent=True) or {}
    focus_area = (payload.get("focus_area") or "").strip()
    difficulty = (payload.get("difficulty") or "").strip()

    if not focus_area or not difficulty:
        return jsonify({"ok": False, "error": "focus_area and difficulty are required"}), 400

    return jsonify({"ok": True, "result": generate_drill(focus_area, difficulty)})

@lab_bp.post("/cognitive/report")
def cognitive_report():
    payload = request.get_json(silent=True) or {}
    goal = (payload.get("goal") or "").strip()
    current_state = (payload.get("current_state") or "").strip()
    target_state = (payload.get("target_state") or "").strip()

    if not goal or not current_state or not target_state:
        return jsonify({"ok": False, "error": "goal, current_state, and target_state are required"}), 400

    return jsonify({"ok": True, "result": generate_report(goal, current_state, target_state)})

@lab_bp.get("/cognitive/runs")
def cognitive_runs():
    return jsonify({"ok": True, "items": get_recent_cognitive_runs(limit=100)})

