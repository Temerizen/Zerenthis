from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

health = Blueprint("health", __name__)

@health.route("/health/log", methods=["POST"])
def log():
    data = request.get_json() or {}
    user = data.get("user", "default")

    db = read("health_system")
    db.setdefault(user, []).append(data)
    write("health_system", db)

    return jsonify({"ok": True})

@health.route("/health/get", methods=["GET"])
def get():
    user = request.args.get("user", "default")
    return jsonify({"ok": True, "data": read("health_system").get(user, [])})
