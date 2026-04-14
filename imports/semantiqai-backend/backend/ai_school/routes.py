import os
from flask import Blueprint, request, jsonify

from .engine import (
    school_overview,
    create_curriculum,
    create_lesson,
    create_quiz,
    record_progress,
    read_progress,
    read_subject
)
from .founder_tools import build_founder_course

ai_school = Blueprint("ai_school", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@ai_school.route("/school/overview", methods=["GET"])
def overview():
    return jsonify(school_overview())

@ai_school.route("/school/subject/<subject_name>", methods=["GET"])
def subject(subject_name):
    data = read_subject(subject_name)
    if not data:
        return jsonify({"error": "subject not found"}), 404
    return jsonify(data)

@ai_school.route("/school/curriculum", methods=["POST"])
def curriculum():
    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    level = (data.get("level") or "beginner").strip()
    goal = (data.get("goal") or "").strip()

    if not subject:
        return jsonify({"error": "subject is required"}), 400

    return jsonify({
        "subject": subject,
        "level": level,
        "goal": goal,
        "curriculum": create_curriculum(subject, level, goal)
    })

@ai_school.route("/school/lesson", methods=["POST"])
def lesson():
    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    topic = (data.get("topic") or "").strip()
    level = (data.get("level") or "beginner").strip()
    mode = (data.get("mode") or "standard").strip()

    if not subject or not topic:
        return jsonify({"error": "subject and topic are required"}), 400

    return jsonify({
        "subject": subject,
        "topic": topic,
        "level": level,
        "mode": mode,
        "lesson": create_lesson(subject, topic, level, mode)
    })

@ai_school.route("/school/quiz", methods=["POST"])
def quiz():
    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    topic = (data.get("topic") or "").strip()
    level = (data.get("level") or "beginner").strip()
    count = int(data.get("count") or 5)

    if not subject or not topic:
        return jsonify({"error": "subject and topic are required"}), 400

    return jsonify({
        "subject": subject,
        "topic": topic,
        "level": level,
        "count": count,
        "quiz": create_quiz(subject, topic, level, count)
    })

@ai_school.route("/school/progress/<user_id>", methods=["GET"])
def progress(user_id):
    return jsonify(read_progress(user_id))

@ai_school.route("/school/progress/update", methods=["POST"])
def progress_update():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "default").strip()
    subject = (data.get("subject") or "general").strip()
    kind = (data.get("kind") or "lesson").strip()
    amount = int(data.get("amount") or 1)

    updated = record_progress(user_id, subject, kind, amount)
    return jsonify(updated)

@ai_school.route("/founder/school/premium-course", methods=["POST"])
def founder_course():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    audience = (data.get("audience") or "").strip()
    monetization_goal = (data.get("monetization_goal") or "").strip()

    if not subject:
        return jsonify({"error": "subject is required"}), 400

    return jsonify({
        "subject": subject,
        "audience": audience,
        "monetization_goal": monetization_goal,
        "course_package": build_founder_course(subject, audience, monetization_goal)
    })
