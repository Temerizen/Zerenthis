import os

DEFAULTS = {
    "APP_ENV": "development",
    "MAX_REQUEST_SIZE": "1048576",
    "REQUEST_TIMEOUT": "30",
    "ENABLE_LOGGING": "true"
}

def ensure_env():
    for k, v in DEFAULTS.items():
        if not os.getenv(k):
            os.environ[k] = v

def get_config():
    return {
        "env": os.getenv("APP_ENV"),
        "max_request_size": int(os.getenv("MAX_REQUEST_SIZE")),
        "timeout": int(os.getenv("REQUEST_TIMEOUT")),
        "logging": os.getenv("ENABLE_LOGGING") == "true"
    }
