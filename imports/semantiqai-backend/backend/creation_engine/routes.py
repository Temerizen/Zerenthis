import os
from flask import Blueprint, request, jsonify

from .engine import *
from .founder_tools import founder_ip_system

creation_engine = Blueprint("creation_engine", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@creation_engine.route("/create/all", methods=["POST"])
def create():
    data = request.json or {}
    return jsonify(create_all(data.get("topic")))

@creation_engine.route("/create/universe", methods=["POST"])
def universe():
    data = request.json or {}
    return jsonify(create_universe_system(data.get("theme")))

@creation_engine.route("/founder/ip", methods=["POST"])
def founder():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.json or {}
    return jsonify(founder_ip_system(data.get("idea")))
