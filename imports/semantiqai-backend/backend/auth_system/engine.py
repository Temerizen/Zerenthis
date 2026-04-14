from .storage import load_users, save_users
from .security import hash_password, verify_password
from .jwt_manager import create_token

def register(username, password, role="user"):
    username = (username or "").strip()
    password = password or ""
    role = (role or "user").strip().lower()

    if not username or not password:
        return {"ok": False, "error": "username and password required"}

    users = load_users()
    if username in users:
        return {"ok": False, "error": "user exists"}

    users[username] = {
        "password": hash_password(password),
        "role": role
    }

    save_users(users)
    return {
        "ok": True,
        "message": "registered",
        "data": {"username": username, "role": role}
    }

def login(username, password):
    username = (username or "").strip()
    password = password or ""

    if not username or not password:
        return {"ok": False, "error": "username and password required"}

    users = load_users()
    user = users.get(username)

    if not user:
        return {"ok": False, "error": "not found"}

    if not verify_password(password, user["password"]):
        return {"ok": False, "error": "invalid"}

    token = create_token(username, user["role"])
    return {
        "ok": True,
        "message": "login successful",
        "data": {
            "token": token,
            "role": user["role"],
            "username": username
        }
    }
