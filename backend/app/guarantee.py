import os
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()
OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ensure_file(content: str, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def fallback_content(topic):
    return f"{topic}\n\nSimple breakdown:\n1. Start simple\n2. Stay consistent\n3. Package value clearly\n\nGenerated safely."

@router.post("/api/generate-safe-pack")
def generate_safe_pack(payload: dict):
    topic = payload.get("topic", "Untitled")

    try:
        from backend.app.main import generate_product_pack
        result = generate_product_pack(payload)

        file_url = None
        if isinstance(result, dict):
            file_url = result.get("file_url")

        # 🔒 GUARANTEE FILE
        if not file_url:
            filename = f"{topic.replace(' ','_')}_{datetime.utcnow().timestamp()}.txt"
            ensure_file(fallback_content(topic), filename)
            file_url = f"/api/file/{filename}"

        return {
            "status": "success",
            "file_url": file_url,
            "fallback_used": file_url.endswith(".txt")
        }

    except Exception as e:
        filename = f"{topic.replace(' ','_')}_fallback.txt"
        ensure_file(fallback_content(topic), filename)

        return {
            "status": "fallback",
            "file_url": f"/api/file/{filename}",
            "error": str(e)
        }
