import os
from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

revenue = Blueprint("revenue", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@revenue.route("/founder/revenue/add", methods=["POST"])
def add():
    if not is_founder(request):
        return jsonify({"ok": False, "error": "unauthorized"}), 403

    data = request.get_json() or {}
    db = read("revenue_engine")
    db.setdefault("entries", []).append(data)
    write("revenue_engine", db)

    return jsonify({"ok": True})

@revenue.route("/founder/revenue/summary", methods=["GET"])
def summary():
    if not is_founder(request):
        return jsonify({"ok": False, "error": "unauthorized"}), 403

    db = read("revenue_engine")
    total = sum([x.get("amount", 0) for x in db.get("entries", [])])

    return jsonify({"ok": True, "data": {"total": total, "entries": db.get("entries", [])}})
