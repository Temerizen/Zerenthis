from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
from datetime import datetime

from .file_index import add_file, load_files

router = APIRouter()
STORAGE = Path("backend/storage")

@router.get("/api/files")
def list_files():
    return load_files()

@router.get("/api/file/{filename}")
def get_file(filename: str):
    path = STORAGE / filename
    if not path.exists():
        return {"error": "file not found"}
    return FileResponse(path)

def save_output(content: str, title: str):
    file_id = str(uuid.uuid4())[:8]
    filename = f"{title.replace(' ','_').lower()}_{file_id}.txt"
    path = STORAGE / filename

    path.write_text(content, encoding="utf-8")

    add_file({
        "filename": filename,
        "title": title,
        "created_at": datetime.utcnow().isoformat()
    })

    return filename
