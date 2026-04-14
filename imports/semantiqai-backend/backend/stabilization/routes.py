from flask import Blueprint, jsonify
from .health import health, readiness
from .backup import create_backup
from .errors import safe_route

stabilization = Blueprint("stabilization", __name__)

@stabilization.route("/health", methods=["GET"])
@safe_route
def health_route():
    return jsonify(health())

@stabilization.route("/ready", methods=["GET"])
@safe_route
def ready_route():
    return jsonify(readiness())

@stabilization.route("/backup", methods=["POST"])
@safe_route
def backup_route():
    return jsonify(create_backup())
