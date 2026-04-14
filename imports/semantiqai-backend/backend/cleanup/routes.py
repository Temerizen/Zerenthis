from flask import Blueprint, jsonify
from backend.cleanup.report import generate_cleanup_report

cleanup = Blueprint("cleanup", __name__)

@cleanup.route("/cleanup/report", methods=["GET"])
def report():
    return jsonify({
        "ok": True,
        "data": generate_cleanup_report()
    })
