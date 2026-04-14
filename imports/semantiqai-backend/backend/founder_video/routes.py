import os
from flask import Blueprint, request, jsonify
from .pipeline import build_founder_video

founder_video = Blueprint("founder_video", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def _authorized(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@founder_video.route("/founder/auto-video", methods=["POST"])
def auto_video():
    if not _authorized(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "").strip()
    style = (data.get("style") or "viral faceless youtube").strip()

    if not topic:
        return jsonify({"error": "topic is required"}), 400

    try:
        result = build_founder_video(topic=topic, style=style)
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
