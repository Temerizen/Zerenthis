import os
from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

calendar = Blueprint("calendar", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@calendar.route("/founder/calendar/add", methods=["POST"])
def add():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    data = request.get_json() or {}
    db = read("content_calendar")
    db.setdefault("items", []).append(data)
    write("content_calendar", db)

    return jsonify({"ok": True})

@calendar.route("/founder/calendar/get", methods=["GET"])
def get():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    return jsonify({"ok": True, "data": read("content_calendar").get("items", [])})
