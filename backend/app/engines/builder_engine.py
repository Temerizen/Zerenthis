import json, uuid
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
GEN_PATH = ROOT / "backend/app/generated"

def run(payload):
    GEN_PATH.mkdir(parents=True, exist_ok=True)

    created = []

    for i in range(2):
        pid = uuid.uuid4().hex

        file_path = GEN_PATH / f"system_{pid}.py"

        content = f"""
# Zerenthis Generated System

def run(input_data=None):
    return {{
        "id": "{pid}",
        "status": "active",
        "type": "auto_generated_tool"
    }}
"""

        file_path.write_text(content, encoding="utf-8")

        created.append(str(file_path))

    return {{
        "status": "systems_created",
        "count": len(created),
        "files": created
    }}
