from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read

analytics = Blueprint("analytics", __name__)

@analytics.route("/analytics/summary", methods=["GET"])
def summary():
    user = request.args.get("user", "default")

    return jsonify({
        "ok": True,
        "data": {
            "finance_entries": len(read("finance_system").get(user, [])),
            "health_logs": len(read("health_system").get(user, [])),
            "notes": len(read("knowledge_vault").get(user, [])),
            "writing_docs": len(read("writing_studio").get(user, []))
        }
    })
