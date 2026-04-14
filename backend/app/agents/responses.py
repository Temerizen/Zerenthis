def ok(data=None, message="ok"):
    return {
        "ok": True,
        "message": message,
        "data": data or {}
    }

def fail(message="error", code=400, error_type="error", extra=None):
    return {
        "ok": False,
        "error": {
            "message": message,
            "type": error_type,
            "code": code,
            "extra": extra or {}
        }
    }

