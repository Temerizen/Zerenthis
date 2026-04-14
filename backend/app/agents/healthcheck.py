import os
from dotenv import load_dotenv

load_dotenv()

def run_checks():
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    jwt_secret = (os.getenv("JWT_SECRET") or "").strip()
    founder_user = (os.getenv("FOUNDER_USERNAME") or "").strip()
    founder_pass = (os.getenv("FOUNDER_PASSWORD") or "").strip()
    port = (os.getenv("PORT") or "5000").strip()

    checks = {
        "openai_key_present": bool(api_key),
        "jwt_secret_present": bool(jwt_secret),
        "founder_username_present": bool(founder_user),
        "founder_password_present": bool(founder_pass),
        "port_present": bool(port),
        "env_ok": all([api_key, jwt_secret, founder_user, founder_pass, port])
    }
    return checks


