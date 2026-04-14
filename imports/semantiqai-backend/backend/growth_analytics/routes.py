import os
from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read

growth = Blueprint("growth", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@growth.route("/founder/growth/summary", methods=["GET"])
def summary():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    return jsonify({
        "ok": True,
        "data": {
            "users": len(read("knowledge_vault")),
            "content": len(read("writing_studio")),
            "activity": len(read("execution_engine"))
        }
    })
