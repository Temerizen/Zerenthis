import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
PLATFORM_DIR = BACKEND_DIR / "platform"
DATA_DIR = PLATFORM_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
CACHE_DIR = DATA_DIR / "cache"
EXPORT_DIR = DATA_DIR / "exports"
METRICS_DIR = DATA_DIR / "metrics"

for path in [DATA_DIR, LOG_DIR, CACHE_DIR, EXPORT_DIR, METRICS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

def env(name: str, default=None):
    return os.getenv(name, default)

def to_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")

def to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default

class Settings:
    APP_NAME = env("APP_NAME", "SemantiqAI Ascension")
    APP_ENV = env("APP_ENV", "development")
    HOST = env("APP_HOST", "127.0.0.1")
    PORT = to_int(env("APP_PORT", "5000"), 5000)
    DEBUG = to_bool(env("APP_DEBUG", "false"), False)
    SECRET_KEY = env("SECRET_KEY", env("JWT_SECRET", "CHANGE_ME_SECRET"))
    JWT_SECRET = env("JWT_SECRET", "CHANGE_ME_SECRET")
    FOUNDER_KEY = env("FOUNDER_KEY", "Ascension_Overlord_777")
    MAX_REQUEST_SIZE = to_int(env("MAX_REQUEST_SIZE", "1048576"), 1048576)
    ENABLE_LOGGING = to_bool(env("ENABLE_LOGGING", "true"), True)
    ENABLE_CORS = to_bool(env("ENABLE_CORS", "true"), True)
    FRONTEND_ORIGIN = env("FRONTEND_ORIGIN", "http://127.0.0.1:5173")
    VERSION = env("APP_VERSION", "ascension-integrated")

def as_dict():
    return {
        "APP_NAME": Settings.APP_NAME,
        "APP_ENV": Settings.APP_ENV,
        "HOST": Settings.HOST,
        "PORT": Settings.PORT,
        "DEBUG": Settings.DEBUG,
        "MAX_REQUEST_SIZE": Settings.MAX_REQUEST_SIZE,
        "ENABLE_LOGGING": Settings.ENABLE_LOGGING,
        "ENABLE_CORS": Settings.ENABLE_CORS,
        "FRONTEND_ORIGIN": Settings.FRONTEND_ORIGIN,
        "VERSION": Settings.VERSION,
    }
