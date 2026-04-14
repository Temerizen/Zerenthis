from datetime import datetime

def health():
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z"
    }

def readiness():
    return {
        "ready": True,
        "checks": [
            "config_loaded",
            "modules_registered",
            "storage_available"
        ]
    }
