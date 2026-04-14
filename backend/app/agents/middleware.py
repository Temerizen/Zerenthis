from flask import request, jsonify
from .jwt_manager import decode_token
from .roles import has_permission

def require_auth(required_role="user"):
    def wrapper(func):
        def inner(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "missing token"}), 401

            data = decode_token(token)
            if not data:
                return jsonify({"error": "invalid token"}), 401

            if not has_permission(data["role"], required_role):
                return jsonify({"error": "forbidden"}), 403

            request.user = data
            return func(*args, **kwargs)
        inner.__name__ = func.__name__
        return inner
    return wrapper

