import os
from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

affiliate = Blueprint("affiliate", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@affiliate.route("/founder/affiliate/add", methods=["POST"])
def add():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    data = request.get_json() or {}
    db = read("affiliate_system")
    db.setdefault("partners", []).append(data)
    write("affiliate_system", db)

    return jsonify({"ok": True})

@affiliate.route("/founder/affiliate/get", methods=["GET"])
def get():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    return jsonify({"ok": True, "data": read("affiliate_system").get("partners", [])})
