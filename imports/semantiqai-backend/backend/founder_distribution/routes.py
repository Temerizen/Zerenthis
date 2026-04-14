import os
from flask import Blueprint, request, jsonify
from .pipeline import full_distribution_pipeline

founder_distribution = Blueprint("founder_distribution", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def auth(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@founder_distribution.route("/founder/distribute", methods=["POST"])
def distribute():
    if not auth(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.json or {}
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "topic required"}), 400

    try:
        result = full_distribution_pipeline(topic)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
