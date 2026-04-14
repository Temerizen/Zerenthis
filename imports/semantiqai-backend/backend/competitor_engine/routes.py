import os
from flask import Blueprint, request, jsonify

competitor = Blueprint("competitor", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@competitor.route("/founder/competitor/analyze", methods=["POST"])
def analyze():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    data = request.get_json() or {}
    name = data.get("name", "unknown")

    return jsonify({
        "ok": True,
        "data": {
            "competitor": name,
            "strengths": ["brand", "distribution"],
            "weaknesses": ["innovation gap"],
            "opportunities": ["AI automation leverage"]
        }
    })
