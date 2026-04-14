from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

finance = Blueprint("finance", __name__)

@finance.route("/finance/add", methods=["POST"])
def add():
    data = request.get_json() or {}
    user = data.get("user", "default")
    entry = data.get("entry", {})

    db = read("finance_system")
    db.setdefault(user, []).append(entry)
    write("finance_system", db)

    return jsonify({"ok": True, "data": db[user]})

@finance.route("/finance/get", methods=["GET"])
def get():
    user = request.args.get("user", "default")
    return jsonify({"ok": True, "data": read("finance_system").get(user, [])})
