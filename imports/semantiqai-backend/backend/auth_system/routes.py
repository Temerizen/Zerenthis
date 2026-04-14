from flask import Blueprint, request, jsonify
from .engine import register, login
from .middleware import require_auth

auth_system = Blueprint("auth_system", __name__)

@auth_system.route("/auth/register", methods=["POST"])
def reg():
    data = request.get_json(silent=True) or {}
    return jsonify(register(data.get("username"), data.get("password"), data.get("role", "user")))

@auth_system.route("/auth/login", methods=["POST"])
def log():
    data = request.get_json(silent=True) or {}
    return jsonify(login(data.get("username"), data.get("password")))

@auth_system.route("/auth/me", methods=["GET"])
@require_auth("user")
def me():
    return jsonify({"ok": True, "data": request.user})

@auth_system.route("/auth/admin", methods=["GET"])
@require_auth("admin")
def admin():
    return jsonify({"ok": True, "message": "admin access granted"})

@auth_system.route("/auth/founder", methods=["GET"])
@require_auth("founder")
def founder():
    return jsonify({"ok": True, "message": "founder access granted"})
