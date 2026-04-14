from flask import Blueprint, jsonify, request
from backend.factory.content_factory import (
    generate_youtube_script,
    generate_social_post,
    generate_pdf_brief,
    generate_email_draft,
    generate_thumbnail_brief,
    generate_full_bundle,
    generate_batch,
)
from backend.factory.run_log import get_recent_content_runs

factory_bp = Blueprint("factory", __name__)

@factory_bp.post("/factory/youtube")
def factory_youtube():
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return jsonify({"ok": False, "error": "Topic is required"}), 400
    return jsonify({"ok": True, "result": generate_youtube_script(topic)})

@factory_bp.post("/factory/social")
def factory_social():
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return jsonify({"ok": False, "error": "Topic is required"}), 400
    return jsonify({"ok": True, "result": generate_social_post(topic)})

@factory_bp.post("/factory/pdf")
def factory_pdf():
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return jsonify({"ok": False, "error": "Topic is required"}), 400
    return jsonify({"ok": True, "result": generate_pdf_brief(topic)})

@factory_bp.post("/factory/email")
def factory_email():
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return jsonify({"ok": False, "error": "Topic is required"}), 400
    return jsonify({"ok": True, "result": generate_email_draft(topic)})

@factory_bp.post("/factory/thumbnail")
def factory_thumbnail():
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return jsonify({"ok": False, "error": "Topic is required"}), 400
    return jsonify({"ok": True, "result": generate_thumbnail_brief(topic)})

@factory_bp.post("/factory/full-bundle")
def factory_full_bundle():
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return jsonify({"ok": False, "error": "Topic is required"}), 400
    return jsonify({"ok": True, "result": generate_full_bundle(topic)})

@factory_bp.post("/factory/batch")
def factory_batch():
    payload = request.get_json(silent=True) or {}
    topics = payload.get("topics") or []
    if not isinstance(topics, list) or not topics:
        return jsonify({"ok": False, "error": "topics must be a non-empty list"}), 400
    return jsonify({"ok": True, "result": generate_batch(topics)})

@factory_bp.get("/factory/runs")
def factory_runs():
    return jsonify({"ok": True, "items": get_recent_content_runs(limit=100)})
