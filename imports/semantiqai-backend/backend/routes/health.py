from flask import Blueprint, jsonify
from backend.core.config import APP_NAME, APP_ENV

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health():
    return jsonify({
        "ok": True,
        "app": APP_NAME,
        "env": APP_ENV,
        "status": "healthy"
    })

@health_bp.get("/status")
def status():
    return jsonify({
        "ok": True,
        "message": "SemantiqAI foundation online"
    })
