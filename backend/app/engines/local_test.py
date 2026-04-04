from pathlib import Path
from datetime import datetime

def run():
    path = Path("backend/app/generated/LIVE_TEST.py")
    path.parent.mkdir(parents=True, exist_ok=True)

    content = f"""
# LIVE BUILD TEST
time = "{datetime.utcnow().isoformat()}"

def run():
    return "Zerenthis is building locally"
"""

    path.write_text(content, encoding="utf-8")

    return {"status": "file_created", "file": str(path)}
