from pathlib import Path
from datetime import datetime

def run(payload=None):
    path = Path("backend/app/generated/LIVE_TEST.py")
    path.parent.mkdir(parents=True, exist_ok=True)

    content = f"""
# LIVE TEST FILE
timestamp = "{datetime.utcnow().isoformat()}"

def run():
    return "Zerenthis is alive and building"
"""

    path.write_text(content, encoding="utf-8")

    return {"status": "created", "file": str(path)}
