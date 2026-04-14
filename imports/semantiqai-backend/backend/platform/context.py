from flask import request

def get_user():
    return getattr(request, "user", {
        "username": "guest",
        "role": "guest"
    })

def is_founder():
    return get_user().get("role") == "founder"

def is_admin():
    return get_user().get("role") in ["admin", "founder"]
