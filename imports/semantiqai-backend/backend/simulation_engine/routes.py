import os
from flask import Blueprint, request, jsonify

from .engine import *
from .founder_tools import founder_simulation

simulation_engine = Blueprint("simulation_engine", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@simulation_engine.route("/simulate", methods=["POST"])
def simulate():
    data = request.json or {}
    return jsonify(run_simulation(data.get("context"), data.get("decision")))

@simulation_engine.route("/simulate/strategy", methods=["POST"])
def strategy():
    data = request.json or {}
    return jsonify(run_strategy(data.get("situation")))

@simulation_engine.route("/simulate/tree", methods=["POST"])
def tree():
    data = request.json or {}
    return jsonify(run_tree(data.get("situation")))

@simulation_engine.route("/simulate/hypothesis", methods=["POST"])
def hypothesis():
    data = request.json or {}
    return jsonify(run_hypothesis(data.get("topic")))

@simulation_engine.route("/founder/simulate", methods=["POST"])
def founder():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.json or {}
    return jsonify(founder_simulation(data.get("command")))
