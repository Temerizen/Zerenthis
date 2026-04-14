from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

life = Blueprint("life", __name__)

@life.route("/life/set", methods=["POST"])
def set_data():
    data = request.get_json() or {}
    user = data.get("user", "default")

    db = read("life_system")
    db[user] = data
    write("life_system", db)

    return jsonify({"ok": True})

@life.route("/life/get", methods=["GET"])
def get_data():
    user = request.args.get("user", "default")
    return jsonify({"ok": True, "data": read("life_system").get(user, {})})
