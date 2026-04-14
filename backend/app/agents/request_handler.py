from functools import wraps
from flask import request, jsonify
from .responses import ok, fail

def handle_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            data = request.get_json(silent=True) or {}
            result = func(data, *args, **kwargs)

            if isinstance(result, dict) and "ok" in result:
                return jsonify(result)

            return jsonify(ok(result))

        except Exception as e:
            return jsonify(fail(str(e), 500, "internal_error")), 500

    return wrapper

