import os
from flask import Blueprint, request, jsonify

audience = Blueprint("audience", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@audience.route("/founder/audience/profile", methods=["GET"])
def profile():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    return jsonify({
        "ok": True,
        "data": {
            "segments": ["creators", "students", "builders"],
            "top_interests": ["money", "AI", "growth"],
            "engagement_score": 87
        }
    })
