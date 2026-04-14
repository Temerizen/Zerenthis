import os
from flask import Blueprint, request, jsonify

from .engine import run_session
from .founder_tools import founder_cognition_boost

cognitive_lab = Blueprint("cognitive_lab", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@cognitive_lab.route("/cognitive/start", methods=["POST"])
def start():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    type = data.get("type", "logic")
    difficulty = data.get("difficulty", "medium")

    drill = run_session(user_id, type, difficulty)
    return jsonify(drill)

@cognitive_lab.route("/cognitive/submit", methods=["POST"])
def submit():
    data = request.json or {}
    user_id = data.get("user_id")
    type = data.get("type")
    user_answer = data.get("user_answer")
    correct_answer = data.get("correct_answer")

    result = run_session(user_id, type, "medium", user_answer, correct_answer)
    return jsonify(result)

@cognitive_lab.route("/founder/cognition", methods=["GET"])
def founder():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    return jsonify({"session": founder_cognition_boost()})
