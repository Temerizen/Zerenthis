from .config import ensure_env
from .logger import log_event

def startup_check():
    ensure_env()
    log_event("startup", {"status": "initialized"})
    return True
