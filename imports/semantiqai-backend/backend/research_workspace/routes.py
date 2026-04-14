from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

research = Blueprint("research", __name__)

@research.route("/research/save", methods=["POST"])
def save():
    data = request.get_json() or {}
    user = data.get("user", "default")

    db = read("research_workspace")
    db.setdefault(user, []).append(data)
    write("research_workspace", db)

    return jsonify({"ok": True})

@research.route("/research/get", methods=["GET"])
def get():
    user = request.args.get("user", "default")
    return jsonify({"ok": True, "data": read("research_workspace").get(user, [])})
