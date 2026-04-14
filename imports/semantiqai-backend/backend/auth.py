import os
import datetime
import jwt
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("JWT_SECRET", "change_me_now")

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password, password_hash)

def create_token(uid, role):
    payload = {
        "uid": uid,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def get_auth_payload():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header.split(" ", 1)[1].strip()
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception:
        return None

def get_user_id():
    payload = get_auth_payload()
    return payload.get("uid") if payload else None

def get_user_role():
    payload = get_auth_payload()
    return payload.get("role") if payload else None

