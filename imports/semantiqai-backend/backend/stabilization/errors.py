from flask import jsonify
from .logger import log_event

def safe_route(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_event("error", {"message": str(e)})
            return jsonify({
                "error": "internal_error",
                "message": str(e)
            }), 500
    wrapper.__name__ = func.__name__
    return wrapper
