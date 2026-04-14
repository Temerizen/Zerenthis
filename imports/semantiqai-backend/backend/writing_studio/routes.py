from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

writing = Blueprint("writing", __name__)

@writing.route("/writing/save", methods=["POST"])
def save():
    data = request.get_json() or {}
    user = data.get("user", "default")

    db = read("writing_studio")
    db.setdefault(user, []).append(data)
    write("writing_studio", db)

    return jsonify({"ok": True})

@writing.route("/writing/get", methods=["GET"])
def get():
    user = request.args.get("user", "default")
    return jsonify({"ok": True, "data": read("writing_studio").get(user, [])})
