from flask import Blueprint, send_from_directory
from pathlib import Path

ui_bp = Blueprint("ui", __name__)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

@ui_bp.get("/app")
def ui_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@ui_bp.get("/app/<path:filename>")
def ui_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

