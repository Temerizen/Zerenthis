from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

vault = Blueprint("vault", __name__)

@vault.route("/vault/save", methods=["POST"])
def save():
    data = request.get_json() or {}
    user = data.get("user", "default")

    db = read("knowledge_vault")
    db.setdefault(user, []).append(data)
    write("knowledge_vault", db)

    return jsonify({"ok": True})

@vault.route("/vault/get", methods=["GET"])
def get():
    user = request.args.get("user", "default")
    return jsonify({"ok": True, "data": read("knowledge_vault").get(user, [])})
