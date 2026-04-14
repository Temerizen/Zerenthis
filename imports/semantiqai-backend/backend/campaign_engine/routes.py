import os
from flask import Blueprint, request, jsonify
from backend.platform.unified_storage import read, write

campaign = Blueprint("campaign", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@campaign.route("/founder/campaign/create", methods=["POST"])
def create():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    data = request.get_json() or {}
    db = read("campaign_engine")
    db.setdefault("campaigns", []).append(data)
    write("campaign_engine", db)

    return jsonify({"ok": True, "data": data})

@campaign.route("/founder/campaign/list", methods=["GET"])
def list():
    if not is_founder(request):
        return jsonify({"ok": False}), 403

    return jsonify({"ok": True, "data": read("campaign_engine").get("campaigns", [])})
