from flask import Blueprint, request, jsonify
import os

from .factory import generate_batch

founder_empire = Blueprint('founder_empire', __name__)

FOUNDER_KEY = os.getenv("FOUNDER_KEY", "ascension_founder_key")

def check_key(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@founder_empire.route("/founder/generate", methods=["POST"])
def generate():
    if not check_key(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.json
    topics = data.get("topics", [])

    results = generate_batch(topics)

    return jsonify(results)
